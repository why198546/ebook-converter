#!/usr/bin/env python3
"""
PDF conversion helper using reportlab directly.
Converts EPUB to HTML, then uses reportlab to create PDF with proper Chinese font and image support.
"""
import os
import tempfile
import zipfile
from html.parser import HTMLParser

from ebook_converter.main import run as ebook_convert_run


class EPUBContentExtractor(HTMLParser):
    """Extract text content and images from HTML files in EPUB, preserving inline formatting."""
    def __init__(self, css_styles=None, debug=False):
        super().__init__()
        self.content = []  # List of ('text', html_text, heading_level, styles_dict), ('image', src), or ('pagebreak',)
        self.current_html = []  # Store HTML fragments with inline tags
        self.in_body = False
        self.current_tag = None
        self.heading_level = 0  # Track heading levels for page breaks
        self.debug = debug
        self.img_count = 0
        self.tag_stack = []  # Track nested tags for proper closing
        self.skip_tags = {'script', 'style', 'head', 'meta', 'link'}
        self.in_paragraph = False  # Track if we're inside a paragraph
        self.css_styles = css_styles or {}  # CSS class definitions
        self.current_para_styles = {}  # Styles for current paragraph (from class attribute)
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attrs_dict = dict(attrs)
        
        if tag in self.skip_tags:
            return
            
        if tag == 'body':
            self.in_body = True
            return
            
        if not self.in_body:
            return
            
        if tag == 'img':
            # Flush text before image
            self._flush_current_html()
            if 'src' in attrs_dict:
                self.img_count += 1
                if self.debug and self.img_count <= 5:
                    print(f"DEBUG: Found img {self.img_count}: {attrs_dict['src']}")
                self.content.append(('image', attrs_dict['src']))
        elif tag == 'image':
            # SVG <image> tag
            self._flush_current_html()
            img_src = attrs_dict.get('xlink:href') or attrs_dict.get('href')
            if img_src:
                self.img_count += 1
                if self.debug:
                    print(f"DEBUG: Found SVG image {self.img_count}: {img_src}")
                self.content.append(('image', img_src))
        elif tag in ['h1', 'h2']:
            # Major headings - flush and add page break
            self._flush_current_html()
            if self.content:  # Don't add page break before first heading
                self.content.append(('pagebreak',))
            self.heading_level = int(tag[1])
            self.in_paragraph = True
        elif tag in ['h3', 'h4', 'h5', 'h6']:
            # Minor headings
            self._flush_current_html()
            self.heading_level = int(tag[1])
            self.in_paragraph = True
        elif tag == 'p':
            # Start new paragraph
            self._flush_current_html()
            self.in_paragraph = True
            # Get styles from class attribute
            class_name = attrs_dict.get('class', '')
            self.current_para_styles = self._get_styles_from_class(class_name)
            # Also check inline style
            inline_style = attrs_dict.get('style', '')
            if inline_style:
                # Extract inline styles and merge
                if 'text-indent' in inline_style:
                    import re
                    match = re.search(r'text-indent:\s*([^;]+)', inline_style)
                    if match:
                        self.current_para_styles['text-indent'] = match.group(1).strip()
                if 'text-align' in inline_style:
                    import re
                    match = re.search(r'text-align:\s*([^;]+)', inline_style)
                    if match:
                        self.current_para_styles['text-align'] = match.group(1).strip()
        elif tag == 'br':
            # Line break
            self.current_html.append('<br/>')
        elif tag in ['b', 'strong']:
            # Bold text
            self.tag_stack.append(tag)
            self.current_html.append('<b>')
        elif tag in ['i', 'em']:
            # Italic text
            self.tag_stack.append(tag)
            self.current_html.append('<i>')
        elif tag == 'span':
            # Check for color in style attribute or CSS class
            style = attrs_dict.get('style', '')
            color = self._extract_color(style)
            
            # If no inline style, check CSS class
            if not color:
                class_name = attrs_dict.get('class', '')
                color = self._get_color_from_class(class_name)
            
            if color:
                self.tag_stack.append(('span', color))
                self.current_html.append(f'<font color="{color}">')
            else:
                self.tag_stack.append('span')
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # Check for color in headings too
            style = attrs_dict.get('style', '')
            color = self._extract_color(style)
            if not color:
                class_name = attrs_dict.get('class', '')
                color = self._get_color_from_class(class_name)
            
            if color and self.in_paragraph:
                # Apply color to heading
                self.current_html.append(f'<font color="{color}">')
                self.tag_stack.append(('heading_color', color))
        elif tag == 'div':
            # Check for page break
            elem_id = attrs_dict.get('id', '')
            style = attrs_dict.get('style', '')
            if 'calibre_pb' in elem_id or 'pagebreak' in elem_id.lower() or 'page-break' in style.lower():
                self._flush_current_html()
                self.content.append(('pagebreak',))
    
    def _extract_color(self, style):
        """Extract color from CSS style string."""
        import re
        # Look for color: value
        match = re.search(r'color:\s*([^;]+)', style)
        if match:
            color = match.group(1).strip()
            # Normalize color names
            color_map = {
                'orange': 'orange',
                'red': 'red',
                'blue': 'blue',
                'green': 'green',
                'gray': 'gray',
                'grey': 'gray',
                'black': 'black',
                'white': 'white',
            }
            return color_map.get(color.lower(), color)
        return None
    
    def _get_color_from_class(self, class_name):
        """Get color from CSS class definition."""
        if not class_name or not self.css_styles:
            return None
        
        # class_name might be space-separated (multiple classes)
        classes = class_name.split()
        for cls in classes:
            # Try with and without dot prefix
            for key in [f'.{cls}', cls]:
                if key in self.css_styles:
                    style_dict = self.css_styles[key]
                    if 'color' in style_dict:
                        return style_dict['color']
        return None
    
    def _get_styles_from_class(self, class_name):
        """Get all style properties from CSS class definition."""
        if not class_name or not self.css_styles:
            return {}
        
        # class_name might be space-separated (multiple classes)
        # Merge styles from all classes
        merged_styles = {}
        classes = class_name.split()
        for cls in classes:
            # Try with and without dot prefix
            for key in [f'.{cls}', cls]:
                if key in self.css_styles:
                    merged_styles.update(self.css_styles[key])
        return merged_styles
    
    def _flush_current_html(self):
        """Flush current HTML text to content list"""
        if self.current_html:
            html_text = ''.join(self.current_html).strip()
            if html_text:
                # Include styles_dict in content tuple
                self.content.append(('text', html_text, self.heading_level, self.current_para_styles.copy()))
            self.current_html = []
            self.current_para_styles = {}  # Reset for next paragraph
            self.heading_level = 0
            self.in_paragraph = False
    
    def handle_endtag(self, tag):
        if tag == 'body':
            self.in_body = False
            self._flush_current_html()
            return
            
        if tag in self.skip_tags or not self.in_body:
            return
            
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # End heading - flush immediately
            self._flush_current_html()
        elif tag == 'p':
            # End paragraph - flush
            self._flush_current_html()
        elif tag in ['b', 'strong']:
            self.current_html.append('</b>')
            if self.tag_stack and self.tag_stack[-1] in ['b', 'strong']:
                self.tag_stack.pop()
        elif tag in ['i', 'em']:
            self.current_html.append('</i>')
            if self.tag_stack and self.tag_stack[-1] in ['i', 'em']:
                self.tag_stack.pop()
        elif tag == 'span':
            if self.tag_stack:
                last_tag = self.tag_stack[-1]
                if isinstance(last_tag, tuple) and last_tag[0] == 'span':
                    # Had color
                    self.current_html.append('</font>')
                    self.tag_stack.pop()
                elif last_tag == 'span':
                    self.tag_stack.pop()
    
    def handle_data(self, data):
        if self.in_body and data.strip():
            # Escape XML special characters for reportlab
            text = data.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            self.current_html.append(text)


def parse_css_for_colors(css_content):
    """
    Parse CSS content and extract styling properties.
    Returns a dict like {'.calibre4': {'color': 'orange', 'text-indent': '2em', 'text-align': 'center'}}
    """
    import re
    styles = {}
    
    # Simple CSS parser - find class definitions and properties
    # Pattern: .classname { ... properties ... }
    class_pattern = r'\.([\w-]+)\s*\{([^}]+)\}'
    
    for match in re.finditer(class_pattern, css_content):
        class_name = match.group(1)
        properties = match.group(2)
        
        style_dict = {}
        
        # Extract color
        color_match = re.search(r'color:\s*([^;}\s]+)', properties)
        if color_match:
            style_dict['color'] = color_match.group(1).strip()
        
        # Extract text-indent
        indent_match = re.search(r'text-indent:\s*([^;}\s]+)', properties)
        if indent_match:
            style_dict['text-indent'] = indent_match.group(1).strip()
        
        # Extract text-align
        align_match = re.search(r'text-align:\s*([^;}\s]+)', properties)
        if align_match:
            style_dict['text-align'] = align_match.group(1).strip()
        
        # Extract margin (for spacing)
        margin_match = re.search(r'margin:\s*([^;}\n]+)', properties)
        if margin_match:
            style_dict['margin'] = margin_match.group(1).strip()
        
        # Extract font-weight (for bold)
        weight_match = re.search(r'font-weight:\s*([^;}\s]+)', properties)
        if weight_match:
            style_dict['font-weight'] = weight_match.group(1).strip()
        
        # Extract font-style (for italic)
        fstyle_match = re.search(r'font-style:\s*([^;}\s]+)', properties)
        if fstyle_match:
            style_dict['font-style'] = fstyle_match.group(1).strip()
        
        # Extract font-size
        fsize_match = re.search(r'font-size:\s*([^;}\s]+)', properties)
        if fsize_match:
            style_dict['font-size'] = fsize_match.group(1).strip()
        
        # Extract font-family
        ffamily_match = re.search(r'font-family:\s*([^;}\n]+)', properties)
        if ffamily_match:
            style_dict['font-family'] = ffamily_match.group(1).strip()
        
        if style_dict:  # Only add if we found some properties
            styles[f'.{class_name}'] = style_dict
    
    return styles


def convert_to_pdf_via_epub(input_file, output_file, verbose=0, quiet=0):
    """
    Convert ebook to PDF using reportlab with Chinese font support.
    
    Process:
    1. Convert input to EPUB
    2. Extract HTML and images from EPUB
    3. Use reportlab to create PDF with proper CJK font support
    
    Args:
        input_file: Path to input ebook file
        output_file: Path to output PDF file
        verbose: Verbosity level (0-2)
        quiet: Quiet level (0-2)
    
    Returns:
        0 on success, non-zero on failure
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
        from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError as exc:
        raise ImportError("reportlab is required for PDF conversion. Install with: pip install reportlab") from exc
    
    # Helper functions for CSS to reportlab conversion
    def parse_indent(indent_str, font_size):
        """Convert CSS text-indent to points
        
        Args:
            indent_str: CSS value like '2em', '24pt', '16px'
            font_size: Current font size in points
            
        Returns:
            Float value in points
        """
        if not indent_str:
            return 0
        
        indent_str = indent_str.strip().lower()
        
        # Handle 'em' units (relative to font size)
        if 'em' in indent_str:
            try:
                em_value = float(indent_str.replace('em', '').strip())
                return em_value * font_size
            except ValueError:
                return 0
        
        # Handle 'pt' units (points, direct)
        if 'pt' in indent_str:
            try:
                return float(indent_str.replace('pt', '').strip())
            except ValueError:
                return 0
        
        # Handle 'px' units (pixels, approximate as points)
        if 'px' in indent_str:
            try:
                return float(indent_str.replace('px', '').strip())
            except ValueError:
                return 0
        
        # Try to parse as plain number (assume points)
        try:
            return float(indent_str)
        except ValueError:
            return 0
    
    def parse_alignment(align_str):
        """Convert CSS text-align to reportlab alignment constant
        
        Args:
            align_str: CSS value like 'center', 'left', 'right', 'justify'
            
        Returns:
            reportlab alignment constant
        """
        if not align_str:
            return TA_JUSTIFY
        
        align_str = align_str.strip().lower()
        
        if align_str == 'center':
            return TA_CENTER
        elif align_str == 'left':
            return TA_LEFT
        elif align_str == 'right':
            return TA_RIGHT
        elif align_str == 'justify':
            return TA_JUSTIFY
        else:
            return TA_JUSTIFY
    
    def parse_margin(margin_str):
        """Convert CSS margin to points
        
        Args:
            margin_str: CSS value like '1em 0', '12pt', '0.5em'
            
        Returns:
            Tuple of (space_before, space_after) in points
        """
        if not margin_str:
            return (0, 0)
        
        margin_str = margin_str.strip().lower()
        parts = margin_str.split()
        
        if len(parts) >= 2:
            # Format: "1em 0" or "12pt 6pt"
            try:
                before = parse_indent(parts[0], 12)  # Use 12pt as base for em conversion
                after = parse_indent(parts[1], 12)
                return (before, after)
            except (ValueError, IndexError):
                return (0, 0)
        elif len(parts) == 1:
            # Single value applies to all sides
            val = parse_indent(parts[0], 12)
            return (val, val)
        
        return (0, 0)
    
    def parse_font_size(size_str, base_size=12):
        """Convert CSS font-size to points
        
        Args:
            size_str: CSS value like '1.5em', '14pt', '16px', 'larger', 'smaller'
            base_size: Base font size in points (default 12)
            
        Returns:
            Float value in points
        """
        if not size_str:
            return base_size
        
        size_str = size_str.strip().lower()
        
        # Handle 'em' units (relative to base size)
        if 'em' in size_str:
            try:
                em_value = float(size_str.replace('em', '').strip())
                return em_value * base_size
            except ValueError:
                return base_size
        
        # Handle 'pt' units (points, direct)
        if 'pt' in size_str:
            try:
                return float(size_str.replace('pt', '').strip())
            except ValueError:
                return base_size
        
        # Handle 'px' units (pixels, approximate as points)
        if 'px' in size_str:
            try:
                return float(size_str.replace('px', '').strip())
            except ValueError:
                return base_size
        
        # Handle named sizes
        if size_str == 'larger':
            return base_size * 1.2
        elif size_str == 'smaller':
            return base_size * 0.8
        elif size_str == 'xx-small':
            return base_size * 0.6
        elif size_str == 'x-small':
            return base_size * 0.75
        elif size_str == 'small':
            return base_size * 0.9
        elif size_str == 'medium':
            return base_size
        elif size_str == 'large':
            return base_size * 1.2
        elif size_str == 'x-large':
            return base_size * 1.5
        elif size_str == 'xx-large':
            return base_size * 2.0
        
        # Try to parse as plain number (assume points)
        try:
            return float(size_str)
        except ValueError:
            return base_size
    
    try:
        # Create temporary directory for intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert to EPUB first
            epub_path = os.path.join(temp_dir, 'temp.epub')
            
            # Create arguments for EPUB conversion
            class Args:
                def __init__(self, from_file, to_file):
                    self.from_file = from_file
                    self.to_file = to_file
                    self.verbose = verbose
                    self.quiet = quiet
            
            args = Args(input_file, epub_path)
            
            # Convert to EPUB
            if verbose:
                print("1% Converting input to EPUB...")
            
            try:
                result = ebook_convert_run(args)
                if result != 0:
                    print(f"EPUB conversion failed with code {result}")
                    return result
            except SystemExit as se:
                print(f"EPUB conversion failed: {se}")
                return se.code if hasattr(se, 'code') and se.code else 1
            except Exception as exc:
                print(f"EPUB conversion failed with exception: {exc}")
                return 1
            
            if not os.path.exists(epub_path):
                print(f"EPUB file was not created at {epub_path}")
                return 1
            
            if verbose:
                print(f"EPUB output written to {epub_path}")
                print("34% Extracting content from EPUB...")
            
            # Extract content from EPUB
            html_files = []
            image_files = {}
            css_styles = {}  # Store CSS color definitions
            
            with zipfile.ZipFile(epub_path, 'r') as epub:
                # First, extract and parse CSS files for color information
                for name in epub.namelist():
                    if name.endswith('.css'):
                        try:
                            css_content = epub.read(name).decode('utf-8', errors='ignore')
                            parsed_styles = parse_css_for_colors(css_content)
                            css_styles.update(parsed_styles)
                            if verbose and parsed_styles:
                                print(f"Parsed {len(parsed_styles)} color styles from {name}")
                        except Exception as exc:
                            if verbose:
                                print(f"Warning: Could not parse CSS {name}: {exc}")
                
                # Find all HTML/XHTML files and extract all images
                for name in epub.namelist():
                    if name.endswith(('.html', '.xhtml', '.htm')):
                        html_files.append(name)
                    elif name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                        # Extract image with full path as key
                        img_data = epub.read(name)
                        img_basename = os.path.basename(name)
                        img_path = os.path.join(temp_dir, img_basename)
                        with open(img_path, 'wb') as img_file:
                            img_file.write(img_data)
                        # Store with both full name and basename as keys
                        image_files[name] = img_path
                        image_files[img_basename] = img_path
                        # Also store without path separators
                        image_files[name.replace('/', '')] = img_path
                
                if not html_files:
                    print("No HTML files found in EPUB")
                    return 1
                
                # Sort HTML files, but put titlepage first if it exists
                def sort_html_files(files):
                    """Sort HTML files with titlepage/cover first, then others alphabetically."""
                    titlepage = None
                    other_files = []
                    
                    for f in files:
                        basename = os.path.basename(f).lower()
                        if 'titlepage' in basename or basename == 'cover.xhtml' or basename == 'cover.html':
                            titlepage = f
                        else:
                            other_files.append(f)
                    
                    result = []
                    if titlepage:
                        result.append(titlepage)
                    result.extend(sorted(other_files))
                    return result
                
                sorted_html_files = sort_html_files(html_files)
                
                # Parse HTML files to extract content in order
                all_content = []
                
                for i, html_file in enumerate(sorted_html_files):
                    try:
                        html_content = epub.read(html_file).decode('utf-8', errors='ignore')
                        # Enable debug for titlepage and 6th file
                        is_titlepage = 'titlepage' in os.path.basename(html_file).lower()
                        # Pass CSS styles to parser
                        parser = EPUBContentExtractor(
                            css_styles=css_styles,
                            debug=(verbose > 0 and (i == 5 or is_titlepage))
                        )
                        parser.feed(html_content)
                        
                        if verbose and (i == 5 or is_titlepage):
                            print(f"DEBUG: File {html_file} had {parser.img_count} images")
                            image_items = [item for item in parser.content if item[0] == 'image']
                            print(f"DEBUG: parser.content has {len(image_items)} image items")
                            if image_items:
                                print(f"DEBUG: First image: {image_items[0]}")
                        
                        all_content.extend(parser.content)
                        
                        # Add page break between HTML files (except after the last one)
                        # This preserves the EPUB's natural page structure
                        if i < len(sorted_html_files) - 1 and parser.content:
                            # Only add if the file had content and it's not already ending with a pagebreak
                            if parser.content and parser.content[-1][0] != 'pagebreak':
                                all_content.append(('pagebreak',))
                    except Exception as exc:
                        if verbose:
                            print(f"Warning: Failed to parse {html_file}: {exc}")
                        continue
            
            # Count items for progress reporting
            text_count = sum(1 for item in all_content if item[0] == 'text')
            image_count = sum(1 for item in all_content if item[0] == 'image')
            pagebreak_count = sum(1 for item in all_content if item[0] == 'pagebreak')
            
            if verbose:
                print(f"67% Extracted {text_count} text blocks and {image_count} image references")
                print(f"    Total items: {len(all_content)} (text:{text_count}, img:{image_count}, pb:{pagebreak_count})")
                print(f"    Available image files: {len(set(image_files.values()))}")
                # Debug: check first few items
                print(f"    First 10 item types: {[item[0] for item in all_content[:10]]}")
                print("Creating PDF...")
            
            # Create PDF using reportlab
            try:
                # Register Chinese font (using system fonts)
                font_registered = False
                chinese_fonts_to_try = [
                    # macOS Chinese fonts - prioritize Kaiti (楷体)
                    ('/System/Library/AssetsV2/com_apple_MobileAsset_Font7/54a2ad3dac6cac875ad675d7d273dc425010a877.asset/AssetData/Kaiti.ttc', 'Kaiti'),
                    ('/System/Library/Fonts/Supplemental/Songti.ttc', 'Songti'),
                    ('/System/Library/Fonts/STSong.ttf', 'STSong'),
                    ('/System/Library/Fonts/STHeiti Medium.ttc', 'STHeiti'),
                    ('/System/Library/Fonts/PingFang.ttc', 'PingFang'),
                    ('/System/Library/Fonts/Hiragino Sans GB.ttc', 'HiraginoSansGB'),
                    # Linux Chinese fonts
                    ('/usr/share/fonts/truetype/arphic/uming.ttc', 'AR PL UMing'),
                    ('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 'WenQuanYi Micro Hei'),
                ]
                
                font_name = 'Helvetica'  # fallback
                for font_path, fname in chinese_fonts_to_try:
                    if os.path.exists(font_path):
                        try:
                            pdfmetrics.registerFont(TTFont(fname, font_path))
                            font_name = fname
                            font_registered = True
                            if verbose:
                                print(f"Using font: {fname}")
                            break
                        except Exception:
                            continue
                
                if not font_registered and verbose:
                    print("Warning: No Chinese font found, using default font (Chinese characters may not display correctly)")
                
                # Create PDF document
                doc = SimpleDocTemplate(
                    output_file,
                    pagesize=A4,
                    rightMargin=2*cm,
                    leftMargin=2*cm,
                    topMargin=2*cm,
                    bottomMargin=2*cm
                )
                
                # Get styles and create custom styles for Chinese
                styles = getSampleStyleSheet()
                
                # Style for normal text
                chinese_style = ParagraphStyle(
                    'Chinese',
                    parent=styles['Normal'],
                    fontName=font_name,
                    fontSize=12,
                    leading=18,
                    alignment=TA_JUSTIFY,
                    spaceAfter=6,
                )
                
                # Style for headings (h1, h2)
                heading_style = ParagraphStyle(
                    'ChineseHeading',
                    parent=styles['Heading1'],
                    fontName=font_name,
                    fontSize=18,
                    leading=24,
                    spaceAfter=12,
                    spaceBefore=12,
                )
                
                # Style for sub-headings (h3)
                subheading_style = ParagraphStyle(
                    'ChineseSubHeading',
                    parent=styles['Heading2'],
                    fontName=font_name,
                    fontSize=14,
                    leading=20,
                    spaceAfter=8,
                    spaceBefore=8,
                )
                
                # Build content from mixed text, images, and page breaks
                story = []
                images_added = 0
                text_added = 0
                pagebreaks_added = 0
                
                for idx, item in enumerate(all_content):
                    content_type = item[0]
                    
                    # Debug first few items and all image items
                    if verbose and (idx < 5 or content_type == 'image'):
                        if content_type == 'image' and idx < 10:  # Only print first 10 images
                            print(f"DEBUG item {idx}: type={content_type}, data={item[1] if len(item) > 1 else 'NO DATA'}")
                        elif idx < 5:
                            print(f"DEBUG item {idx}: type={content_type}, len={len(item)}")
                    
                    if content_type == 'pagebreak':
                        # Add page break
                        story.append(PageBreak())
                        pagebreaks_added += 1
                        
                    elif content_type == 'text':
                        # item is ('text', text_content, heading_level, styles_dict)
                        content_value = item[1]
                        heading_level = item[2] if len(item) > 2 else 0
                        styles_dict = item[3] if len(item) > 3 else {}
                        
                        # Add text paragraph with appropriate style
                        if content_value.strip():
                            try:
                                # Choose base style based on heading level
                                if heading_level in [1, 2]:
                                    base_style = heading_style
                                elif heading_level == 3:
                                    base_style = subheading_style
                                else:
                                    base_style = chinese_style
                                
                                # If we have CSS styles, create a custom style
                                if styles_dict:
                                    custom_style = ParagraphStyle(
                                        f'Custom_{idx}',
                                        parent=base_style
                                    )
                                    
                                    # Apply font-size first (affects other calculations)
                                    current_font_size = base_style.fontSize
                                    if 'font-size' in styles_dict:
                                        new_size = parse_font_size(styles_dict['font-size'], base_style.fontSize)
                                        if new_size > 0:
                                            custom_style.fontSize = new_size
                                            # Adjust leading (line height) proportionally
                                            custom_style.leading = new_size * 1.5
                                            current_font_size = new_size
                                    
                                    # Apply font-family (if specified, use it; otherwise keep base font)
                                    if 'font-family' in styles_dict:
                                        # For now, keep using our registered Chinese font
                                        # In future could register multiple fonts
                                        pass
                                    
                                    # Apply text-indent
                                    if 'text-indent' in styles_dict:
                                        indent_val = parse_indent(styles_dict['text-indent'], current_font_size)
                                        if indent_val > 0:
                                            custom_style.leftIndent = indent_val
                                        elif indent_val < 0:
                                            # Negative indent (hanging indent)
                                            custom_style.firstLineIndent = indent_val
                                    
                                    # Apply text-align
                                    if 'text-align' in styles_dict:
                                        custom_style.alignment = parse_alignment(styles_dict['text-align'])
                                    
                                    # Apply margin
                                    if 'margin' in styles_dict:
                                        space_before, space_after = parse_margin(styles_dict['margin'])
                                        if space_before > 0:
                                            custom_style.spaceBefore = space_before
                                        if space_after > 0:
                                            custom_style.spaceAfter = space_after
                                    
                                    para = Paragraph(content_value, custom_style)
                                else:
                                    para = Paragraph(content_value, base_style)
                                
                                story.append(para)
                                story.append(Spacer(1, 0.2*cm))
                                text_added += 1
                            except Exception as exc:
                                if verbose:
                                    print(f"Warning: Could not add paragraph: {exc}")
                                continue
                    
                    elif content_type == 'image':
                        # Add image
                        # Try multiple variations of the image path
                        content_value = item[1]  # Get image path from tuple
                        img_path = None
                        img_name = os.path.basename(content_value)
                        
                        # Debug first image
                        if verbose and images_added == 0:
                            print(f"DEBUG: First image to add: {content_value}")
                            print(f"DEBUG: Basename: {img_name}")
                            print(f"DEBUG: image_files keys sample: {list(image_files.keys())[:5]}")
                        
                        # Try different path combinations
                        for key in [content_value, img_name, content_value.replace('/', ''), 
                                   content_value.replace('../', ''), content_value.lstrip('./')]:
                            if key in image_files:
                                img_path = image_files[key]
                                break
                        
                        if img_path and os.path.exists(img_path):
                            try:
                                img = RLImage(img_path)
                                # Get original image size
                                from PIL import Image as PILImage
                                pil_img = PILImage.open(img_path)
                                orig_width, orig_height = pil_img.size
                                
                                # Special handling for first image (cover) - make it full page
                                is_cover = (images_added == 0 and idx == 0)
                                
                                if is_cover:
                                    # Full page size minus small margins (A4: 21cm x 29.7cm)
                                    # Use slightly smaller size to fit within reportlab's frame
                                    page_width, page_height = A4
                                    # Account for document margins (2cm on each side)
                                    usable_width = page_width - 4*cm
                                    usable_height = page_height - 4*cm
                                    
                                    aspect = orig_height / orig_width
                                    page_aspect = usable_height / usable_width
                                    
                                    # Fill the usable area while maintaining aspect ratio
                                    if aspect > page_aspect:
                                        # Image is taller, fit to height
                                        new_height = usable_height
                                        new_width = new_height / aspect
                                    else:
                                        # Image is wider, fit to width
                                        new_width = usable_width
                                        new_height = new_width * aspect
                                    
                                    if verbose:
                                        print(f"DEBUG: Cover image sized to {new_width/cm:.1f}cm x {new_height/cm:.1f}cm")
                                else:
                                    # Regular images - fit within content area
                                    max_width = 16*cm
                                    max_height = 20*cm
                                    
                                    aspect = orig_height / orig_width
                                    new_width = min(max_width, orig_width * 0.0352778 * cm)  # px to cm conversion
                                    new_height = new_width * aspect
                                    
                                    # If too tall, scale by height instead
                                    if new_height > max_height:
                                        new_height = max_height
                                        new_width = new_height / aspect
                                
                                img.drawWidth = new_width
                                img.drawHeight = new_height
                                
                                story.append(img)
                                
                                # Don't add spacer after cover image
                                if not is_cover:
                                    story.append(Spacer(1, 0.5*cm))
                                    
                                images_added += 1
                                
                            except Exception as exc:
                                if verbose:
                                    print(f"Warning: Could not add image {img_name}: {exc}")
                        elif verbose and images_added < 10:  # Don't spam warnings
                            print(f"Warning: Image not found: {content_value}")
                
                if verbose:
                    print(f"Added {text_added} text blocks, {images_added} images, and {pagebreaks_added} page breaks to PDF")
                
                # Build PDF
                doc.build(story)
                
                if verbose:
                    print(f"PDF created successfully: {output_file}")
                
                return 0
                
            except Exception as exc:
                print(f"PDF creation failed: {exc}")
                import traceback
                traceback.print_exc()
                return 1
    
    except Exception as exc:
        print(f"PDF conversion failed: {exc}")
        import traceback
        traceback.print_exc()
        return 1
