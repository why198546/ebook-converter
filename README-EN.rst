===============
Ebook converter
===============

**Language / 语言**: `English <README-EN.rst>`_ | `中文 <README.md>`_

---

This is an impudent ripoff of the bits from `Calibre project`_, and is aimed
only for converter thing.

My motivation is to have only the converter for ebooks run from the
commandline, without all of those bells and whistles Calibre has, and with
cleanest more *pythonic* approach.

**New Features:**

- 🌐 **Web Interface** - User-friendly web UI for single and batch conversions
- 📄 **PDF Output Support** - Convert ebooks to PDF with full Chinese font support (Kaiti)
- 🎨 **Enhanced PDF Formatting** - Preserves colors, text alignment, indentation, and font styles from CSS
- 🇨🇳 **Chinese Filename Support** - Properly handles Unicode filenames in downloads
- 🚀 **Background Service** - Easy-to-use service management with ``ebook-convert``, ``ebook-stop`` commands

Requirements
------------

To build and run ebook converter, you'll need:

- Python 3.10 or newer
- `Liberation fonts`_
- setuptools
- ``pdftohtml``, ``pdfinfo`` and ``pdftoppm`` from `poppler`_ project for
  conversion from PDF available in ``$PATH``
- ``libxml2-dev`` and ``libxslt-dev`` as dependencies for format manipulation
  from some of the Calibre code

and several Python packages:

- `beautifulsoup4`_
- `css-parser`_
- `filelock`_
- `flask`_ (for web interface)
- `html2text`_
- `html5-parser`_
- `msgpack`_
- `odfpy`_
- `pillow`_
- `python-dateutil`_
- `reportlab`_ (for PDF generation with Chinese support)
- `setuptools`_
- `tinycss`_

No Python2 support. Even if Calibre probably still is able to run on Python2, I
do not have an intention to support it.


What's supported
----------------

To be able to perform some optimization and make the converter more reliable
and easy to use, first I need to remove some of the features, which are totally
not crucial in my opinion, although they might be re-added later, like, for
instance there is no automatic language translations depending on the locale
settings.

First of all, I'm in the process of getting rid of strongly coupled things to
QT libraries, and GUI code as well. Second, I'll try to minimize all
modifications from third parties (external modules copied into Calibre project
for instance), and make a huge cleanup. I'm not sure if I find time and
strength for doing it completely, but I'll try.

Windows is not currently supported, because of the original spaghetti code.
This may change in the future, after cleanup of mentioned pasta would be
completed.

So called *Kindle periodical* format (which `Amazon has`_ `killed`_ anyway back
in September 2023) is not supported, since all we do care are local files. If
there would be downloaded periodical thing (using Calibre for example), it
would be treated as common book.


Input formats
~~~~~~~~~~~~~

Currently, I've tested the following input formats:

- Microsoft Word 2007 and up (``docx``)
- EPUB, both v2 and v3 (``epub``)
- LibreOffice (``odt``)
- Pure text files (``txt``)
- Several PalmOS (``pdb``) readers support:

  - Plucker
  - Adobe Reader for PalmOS
  - eReader various formats
  - Weasel Reader
  - Haodoo Reader

- Rich Text Format (``rtf``)
- Mobipocket (``mobi``)
- Kindle (``azw3``, ``azw4``, …)
- FictionBook (``fb2``)
- Hyper Text Markup Language (``html``)
- Adobe Portable Document Format (``pdf``)
- Broadband eBooks (shortened as BBeB) (``lrf``)

Note, that old Microsoft doc format is not supported, although old documents
can be fairly easy converted using text processors programs, like Microsoft
Word or LibreOffice to supported formats.


Output formats
~~~~~~~~~~~~~~

Currently, following formats are supported:

- **Adobe Portable Document Format (``pdf``)** - with full Chinese character support (Kaiti font), CSS formatting preservation (colors, alignment, indentation, font styles)
- Broadband eBooks (shortened as BBeB) (``lrf``)
- EPUB v2 (``epub``)
- Mobipocket (``mobi``)
- Microsoft Word (``docx``)
- zipped HTML file with additional assets, like images (``htmlz``)
- Text (``txt``)


Installation
------------

Ebook converter is somewhere in between in alpha and beta stage, therefore I
didn't place it on `pypi`_ yet.

Preferred way for installation is to use virtualenv (or any other virtualenv
managers), i.e:

.. code:: shell-session

   $ python -m venv venv
   $ . venv/bin/activate
   (venv) $ git clone https://github.com/gryf/ebook-converter
   (venv) $ cd ebook-converter
   (venv) $ pip install .

Simple as that. And from now on, you can use the converter.


Usage
-----

Command Line Mode
~~~~~~~~~~~~~~~~~

Traditional command-line conversion:

.. code:: shell-session

   (venv) $ ebook-converter book.docx book.lrf
   (venv) $ ebook-converter book.mobi book.pdf

Web Interface Mode
~~~~~~~~~~~~~~~~~~

For a more user-friendly experience with drag-and-drop support:

.. code:: shell-session

   (venv) $ ebook-convert      # Start the web server
   (venv) $ ebook-stop         # Stop the web server
   (venv) $ ebook-status       # Check server status

The web interface will automatically open in your browser at ``http://127.0.0.1:5001``.

Features of the web interface:

- **Single File Conversion**: Drag and drop files with instant conversion
- **Batch Conversion**: Convert multiple files at once
- **Format Support**: All input/output formats supported
- **Chinese Support**: Proper handling of Chinese filenames and content
- **PDF Features**: High-quality PDF output with Chinese fonts (Kaiti) and CSS formatting preservation

For detailed web interface documentation, see `WEB_INTERFACE.md`_.


PDF Conversion Features
~~~~~~~~~~~~~~~~~~~~~~~

When converting to PDF format, the converter provides:

- **Chinese Font Support**: Built-in Kaiti (楷体) font for proper Chinese character rendering
- **CSS Formatting Preservation**:
  
  - Text colors (from CSS ``color`` property)
  - Text alignment (``text-align``: left, center, right, justify)
  - Text indentation (``text-indent``)
  - Margins (``margin``, ``margin-left``, etc.)
  - Font sizes (supports em, pt, px units and named sizes)
  - Font families and styles (bold, italic)

- **Cover Images**: Automatically includes book covers with proper sizing
- **Chapter Breaks**: Maintains chapter structure with page breaks
- **Unicode Filenames**: Properly handles Chinese and other Unicode characters in filenames


License
-------

This work is licensed on GPL3 license, like the original work. See LICENSE file
for details.

.. _Calibre project: https://calibre-ebook.com/
.. _pypi: https://pypi.python.org
.. _Liberation fonts: https://github.com/liberationfonts/liberation-fonts
.. _Amazon has: https://goodereader.com/blog/kindle/amazon-will-discontinue-newspaper-and-magazine-subscriptions-in-september
.. _killed: https://www.theverge.com/23861370/amazon-kindle-periodicals-unlimited-ended
.. _poppler: https://poppler.freedesktop.org/
.. _beautifulsoup4: https://www.crummy.com/software/BeautifulSoup
.. _css-parser: https://github.com/ebook-utils/css-parser
.. _filelock: https://github.com/tox-dev/py-filelock
.. _html2text: https://github.com/Alir3z4/html2text
.. _html5-parser: https://html5-parser.readthedocs.io
.. _msgpack: https://msgpack.org
.. _odfpy: https://github.com/eea/odfpy
.. _pillow: https://python-pillow.github.io
.. _python-dateutil: https://github.com/dateutil/dateutil
.. _setuptools: https://setuptools.pypa.io
.. _tinycss: http://tinycss.readthedocs.io
.. _flask: https://flask.palletsprojects.com
.. _reportlab: https://www.reportlab.com/opensource/
.. _WEB_INTERFACE.md: WEB_INTERFACE.md
