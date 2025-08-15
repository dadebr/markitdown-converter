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

- **PDF** - Portable Document Format documents
- **PPT/PPTX** - PowerPoint presentations
- **DOCX** - Microsoft Word documents
- **JSON** - JavaScript Object Notation files
- **TXT** - Plain text files
- **CSV** - Comma-Separated Values files
- **XLSX** - Microsoft Excel spreadsheets

### 🛠️ Interface Features

- Intuitive graphical interface developed in Tkinter
- Individual or multiple file selection
- Custom destination directory selection
- Integrated terminal for real-time log viewing
- Progress bar for conversion tracking
- Error handling with informative messages

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
│   └── file_handler.py
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
