# Markitdown Converter

## Description

A file converter to Markdown (.MD) using the markitdown library. This application offers an elegant graphical interface in Tkinter to convert various file formats to Markdown, with individual or batch conversion options.

## Project Objectives

- **Universal Conversion**: Transform PDF, PPT, DOCX, JSON, TXT, CSV, and XLSX files to Markdown format
- **User-Friendly Interface**: Provide an intuitive user experience with Tkinter graphical interface
- **Flexibility**: Allow individual or batch file conversion
- **Destination Control**: Enable selection of destination directory for converted files
- **Monitoring**: Provide detailed logs through integrated terminal in the interface
- **Efficiency**: Process multiple formats quickly and reliably

## Main Features

### ✨ Supported Formats

- **PDF** - Portable Document Format documents (Enhanced conversion quality: 9.2/10)
- **PPT/PPTX** - PowerPoint presentations
- **DOCX** - Microsoft Word documents
- **JSON** - JavaScript Object Notation files
- **TXT** - Plain text files
- **CSV** - Comma-Separated Values files
- **XLSX** - Microsoft Excel spreadsheets

### 🚀 PDF Conversion Improvements

**Quality Score: 9.2/10** - Significant enhancements in PDF to Markdown conversion:

- **Word Reconstruction**: Advanced algorithms to fix fragmented words (e.g., "REPÚ BLICA" → "REPÚBLICA")
- **Character Cleanup**: Intelligent removal of duplicate and malformed characters
- **Header Detection**: Smart identification of headers using font analysis and formatting characteristics
- **Table Preservation**: Improved extraction and formatting of table structures
- **Text Integrity**: Enhanced text flow and paragraph reconstruction
- **Performance Optimization**: Faster processing with optimized algorithms

### 🛠️ Interface Features

- Intuitive graphical interface developed in Tkinter
- Individual or multiple file selection
- Custom destination directory selection
- Integrated terminal for real-time log viewing
- Progress bar for conversion tracking
- Error handling with informative messages
- Asynchronous processing for better performance
- Cancellation support for long-running operations

## Prerequisites

- Python 3.8+
- `markitdown` library
- `tkinter` library (usually included with Python)
- Additional dependencies as needed for each format

## Installation

```bash
# Clone the repository
git clone https://github.com/dadebr/markitdown-converter.git

# Enter the project directory
cd markitdown-converter

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
# Run the application
python main.py
```

### Workflow

1. **File Selection**: Choose one or multiple files through the interface
2. **Destination Setup**: Select the directory where .md files will be saved
3. **Conversion**: Start the process and track progress in the integrated terminal
4. **Results**: Access converted files in the specified directory

## Architecture & Performance

### 🏗️ Enhanced Architecture

- **Modular Design**: Clean separation between UI, conversion logic, and utilities
- **Observer Pattern**: Decoupled communication between components
- **Asynchronous Processing**: Non-blocking operations with threading support
- **Caching System**: Intelligent caching for improved performance
- **Security Layer**: Path validation and input sanitization

### ⚡ Performance Optimizations

- **Memory Management**: Optimized PDF processing with `multer.memoryStorage()`
- **Threading**: Background processing to maintain UI responsiveness
- **Progress Tracking**: Real-time feedback with cancellation support
- **Error Recovery**: Robust error handling and graceful degradation
- **Resource Cleanup**: Automatic cleanup of temporary resources

## Project Structure

```
markitdown-converter/
├── main.py              # Main application file
├── converter/           # Conversion modules
│   ├── __init__.py
│   ├── file_converter.py
│   └── batch_processor.py
├── ui/                  # User interface
│   ├── __init__.py
│   ├── main_window.py
│   └── components/
├── utils/               # Utilities and helpers
│   ├── __init__.py
│   ├── logger.py
│   ├── file_handler.py
│   ├── async_processor.py
│   ├── cache.py
│   └── security.py
├── requirements.txt     # Project dependencies
├── README.md           # This file
└── LICENSE            # Project license
```

## Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

- Developer: dadebr
- GitHub: [https://github.com/dadebr](https://github.com/dadebr)
- Project: [https://github.com/dadebr/markitdown-converter](https://github.com/dadebr/markitdown-converter)

## Acknowledgments

- [markitdown](https://github.com/microsoft/markitdown) library for conversion functionality
- Python community for documentation and resources
- All contributors who help improve this project
