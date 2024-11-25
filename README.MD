# TopG Hustlers University JSON Chat Viewer

## Overview

JSON Chat Viewer is a powerful, user-friendly Python-based tool for viewing and processing JSON chat logs. It provides an interactive GUI for browsing, searching, and analyzing large datasets, especially useful for logs from platforms like Andrew Tate's "The Real World" (formerly Hustler's University).

This tool is free to use. If you wish to fork, modify, or redistribute it, please credit the original author.

---

## Features

- **Drag and Drop Support**: Effortlessly load files or folders by dragging and dropping them into the application.
- **Interactive Sidebar**: Navigate through your loaded JSON files with ease.
- **Tabbed Viewing**: Open multiple JSON files in tabs for side-by-side comparison.
- **Search Toolbar**: Quickly find content within the loaded chat logs.
- **HTML Caching**: Automatically generates HTML caches for faster reloading.
- **Batch Conversion**: Includes a separate script for batch converting JSON files to HTML.
- **Customizable Cache Management**: Clear cache and session data directly from the UI.

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/kicedz/topg_json_chat_viewer.git
   cd topg_json_chat_viewer
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python json_chat_viewer.py
   ```

---

## Usage

### Viewing JSON Files

1. Drag and drop a file or folder into the application window.
2. Select a file from the sidebar to view its content.
3. Use the search toolbar to locate specific entries.
4. NOTE: THE APP CAN HANG FOR LARGE JSONs BE PATIENT

### Batch Conversion

Convert multiple JSON files to HTML using the included converter script:

```bash
python json_to_html_converter.py <input_folder> <output_folder>
```

Example:

```bash
python json_to_html_converter.py "./Public Channels" "./html_output"
```

### Cache Management

- **Clear Cache**: Removes all cached HTML files.
- **Clear Sessions**: Resets the session history and closes all tabs.

---

## Project Structure

```plaintext
.
├── README.MD                # Documentation
├── json_chat_viewer.py      # Main application script
├── json_to_html_converter.py# Batch conversion script
├── session.json             # Session data (automatically managed)
├── .cache/                  # Cache directory (auto-generated, gitignored)
└── .env                     # Environment settings (gitignored)
```

---

## Keywords

- JSON Chat Viewer
- JSON Logs
- Chat Logs Viewer
- Andrew Tate Chat Logs
- Hustler's University
- Python GUI
- PyQt5
- JSON to HTML
- Data Processing
- Batch Converter
- Open Source
- Free to Use

---

## License

This project is free to use. If you fork, modify, or redistribute it, **please credit the author: kicedz**.

---

## Contributing

Pull requests are welcome! If you encounter any issues or have feature requests, please submit them via GitHub.

---
