#!/usr/bin/env python3
"""
Web interface for ebook-converter.
Provides a user-friendly GUI for converting ebooks.
"""
import os
import tempfile
import shutil
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify

# Import the conversion function directly
from ebook_converter.main import run as ebook_convert_run
from ebook_converter.pdf_converter import convert_to_pdf_via_epub

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Supported formats
INPUT_FORMATS = {
    'docx': 'Microsoft Word 2007+',
    'epub': 'EPUB',
    'odt': 'LibreOffice',
    'txt': 'Plain Text',
    'pdb': 'PalmOS',
    'rtf': 'Rich Text Format',
    'mobi': 'Mobipocket',
    'azw3': 'Kindle',
    'azw4': 'Kindle',
    'fb2': 'FictionBook',
    'html': 'HTML',
    'htm': 'HTML',
    'pdf': 'PDF',
    'lrf': 'Broadband eBook',
}

OUTPUT_FORMATS = {
    'pdf': 'PDF (.pdf)',
    'epub': 'EPUB v2 (.epub)',
    'docx': 'Microsoft Word (.docx)',
    'txt': 'Plain Text (.txt)',
}

def allowed_input_file(filename):
    """Check if the input file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in INPUT_FORMATS

def allowed_output_format(format_ext):
    """Check if the output format is allowed."""
    return format_ext.lower() in OUTPUT_FORMATS


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', 
                         input_formats=INPUT_FORMATS,
                         output_formats=OUTPUT_FORMATS)


@app.route('/favicon.ico')
def favicon():
    """Return a simple favicon response to avoid 404 errors."""
    return '', 204  # No Content


@app.route('/convert', methods=['POST'])
def convert():
    """Handle file conversion."""
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    if not allowed_input_file(file.filename):
        return jsonify({'error': f'不支持的输入格式。支持的格式: {", ".join(INPUT_FORMATS.keys())}'}), 400
    
    # Get output format
    output_format = request.form.get('output_format', '').lower()
    if not output_format or not allowed_output_format(output_format):
        return jsonify({'error': f'不支持的输出格式。支持的格式: {", ".join(OUTPUT_FORMATS.keys())}'}), 400
    
    try:
        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Save uploaded file with safe name for temp processing
            input_filename = secure_filename(file.filename)
            input_path = os.path.join(temp_dir, input_filename)
            file.save(input_path)
            
            # Create output filename - preserve original Chinese name, only change extension
            # Get original filename without extension (preserving Chinese characters)
            original_name = Path(file.filename).stem
            output_filename = original_name + '.' + output_format
            # For temp path, use secure filename, but we'll use original for download
            safe_output_filename = secure_filename(output_filename)
            # If secure_filename removed all characters, use a fallback
            if not safe_output_filename or safe_output_filename == '.' + output_format:
                safe_output_filename = 'output.' + output_format
            output_path = os.path.join(temp_dir, safe_output_filename)
            
            # Perform conversion using the converter directly
            # Create arguments object
            class Args:
                def __init__(self, from_file, to_file):
                    self.from_file = from_file
                    self.to_file = to_file
                    self.verbose = 0
                    self.quiet = 0
            
            # Special handling for PDF output (uses weasyprint instead of PyQt5)
            if output_format.lower() == 'pdf':
                try:
                    result_code = convert_to_pdf_via_epub(input_path, output_path, verbose=0, quiet=0)
                    if result_code != 0:
                        error_msg = f'PDF 转换失败，返回码: {result_code}'
                        print(f"[ERROR] PDF conversion failed with code: {result_code}")
                        return jsonify({'error': error_msg}), 500
                except Exception as pdf_error:
                    error_msg = f'PDF 转换出错: {str(pdf_error)}'
                    print(f"[ERROR] PDF conversion error: {str(pdf_error)}")
                    import traceback
                    traceback.print_exc()
                    return jsonify({'error': error_msg}), 500
            else:
                # Standard conversion for other formats
                args = Args(input_path, output_path)
                
                # Call the conversion function directly
                try:
                    result_code = ebook_convert_run(args)
                    if result_code != 0:
                        error_msg = f'转换失败，返回码: {result_code}'
                        print(f"[ERROR] Conversion failed with code: {result_code}")
                        return jsonify({'error': error_msg}), 500
                except SystemExit as se:
                    # Handle sys.exit() calls
                    if se.code != 0:
                        error_msg = f'转换失败，退出码: {se.code}'
                        print(f"[ERROR] Conversion exited with code: {se.code}")
                        return jsonify({'error': error_msg}), 500
            
            # Check if output file was created
            if not os.path.exists(output_path):
                return jsonify({'error': '转换失败，未生成输出文件'}), 500
            
            # Read file into memory before cleanup
            with open(output_path, 'rb') as f:
                file_data = f.read()
            
            # Clean up temp directory
            shutil.rmtree(temp_dir)
            
            # Return file data with filename in JSON response
            # The client-side JavaScript will handle the download with correct filename
            import base64
            return jsonify({
                'success': True,
                'filename': output_filename,
                'data': base64.b64encode(file_data).decode('utf-8'),
                'mimetype': 'application/octet-stream'
            })
        except Exception as inner_e:
            # Clean up temp directory on error
            print(f"[ERROR] Exception during conversion: {str(inner_e)}")
            import traceback
            traceback.print_exc()
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise inner_e
    
    except Exception as e:
        print(f"[ERROR] Outer exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'处理文件时出错: {str(e)}'}), 500


@app.route('/batch')
def batch():
    """Render the batch conversion page."""
    return render_template('batch.html',
                         input_formats=INPUT_FORMATS,
                         output_formats=OUTPUT_FORMATS)


@app.route('/batch-convert', methods=['POST'])
def batch_convert():
    """Handle batch file conversion."""
    if 'files[]' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    files = request.files.getlist('files[]')
    output_format = request.form.get('output_format', '').lower()
    
    if not output_format or not allowed_output_format(output_format):
        return jsonify({'error': f'不支持的输出格式'}), 400
    
    results = []
    
    for file in files:
        if file.filename == '':
            continue
            
        if not allowed_input_file(file.filename):
            results.append({
                'filename': file.filename,
                'status': 'error',
                'message': '不支持的格式'
            })
            continue
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                input_filename = secure_filename(file.filename)
                input_path = os.path.join(temp_dir, input_filename)
                file.save(input_path)
                
                # Preserve original Chinese filename, only change extension
                original_name = Path(file.filename).stem
                output_filename = original_name + '.' + output_format
                # For temp path, use secure filename
                safe_output_filename = secure_filename(output_filename)
                if not safe_output_filename or safe_output_filename == '.' + output_format:
                    safe_output_filename = 'output.' + output_format
                output_path = os.path.join(temp_dir, safe_output_filename)
                
                # Special handling for PDF output
                if output_format.lower() == 'pdf':
                    try:
                        result_code = convert_to_pdf_via_epub(input_path, output_path, verbose=0, quiet=0)
                        if result_code == 0 and os.path.exists(output_path):
                            results.append({
                                'filename': file.filename,
                                'status': 'success',
                                'message': '转换成功',
                                'output_filename': output_filename
                            })
                        else:
                            results.append({
                                'filename': file.filename,
                                'status': 'error',
                                'message': 'PDF 转换失败'
                            })
                    except Exception as pdf_error:
                        results.append({
                            'filename': file.filename,
                            'status': 'error',
                            'message': f'PDF 转换出错: {str(pdf_error)}'
                        })
                else:
                    # Standard conversion for other formats
                    # Create arguments object
                    class Args:
                        def __init__(self, from_file, to_file):
                            self.from_file = from_file
                            self.to_file = to_file
                            self.verbose = 0
                            self.quiet = 0
                    
                    args = Args(input_path, output_path)
                    
                    # Call the conversion function directly
                    try:
                        result_code = ebook_convert_run(args)
                        if result_code == 0 and os.path.exists(output_path):
                            results.append({
                                'filename': file.filename,
                                'status': 'success',
                                'message': '转换成功',
                                'output_filename': output_filename
                            })
                        else:
                            results.append({
                                'filename': file.filename,
                                'status': 'error',
                                'message': '转换失败'
                            })
                    except SystemExit as se:
                        # Handle sys.exit() calls
                        if se.code == 0 and os.path.exists(output_path):
                            results.append({
                                'filename': file.filename,
                                'status': 'success',
                                'message': '转换成功',
                                'output_filename': output_filename
                            })
                        else:
                            results.append({
                                'filename': file.filename,
                                'status': 'error',
                                'message': f'转换失败，退出码: {se.code}'
                            })
        except Exception as e:
            results.append({
                'filename': file.filename,
                'status': 'error',
                'message': str(e)
            })
    
    return jsonify({'results': results})


def main():
    """Run the Flask application."""
    print("Starting ebook-converter web interface...")
    print("Open your browser and navigate to: http://127.0.0.1:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)


if __name__ == '__main__':
    main()
