import sys
import json
import os
import re
import hashlib
import shutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextBrowser, QTabWidget,
    QFileDialog, QMenuBar, QAction, QTreeWidget, QTreeWidgetItem,
    QSplitter, QWidget, QVBoxLayout, QMessageBox, QLineEdit, QToolBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QTextCursor, QTextDocument

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Chat Viewer")
        self.setGeometry(100, 100, 1200, 800)
        if os.path.exists('icon.png'):
            self.setWindowIcon(QIcon('icon.png'))

        self.session_file = 'session.json'
        self.session_files = []

        self.cache_dir = os.path.join(os.path.dirname(__file__), '.cache')
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderHidden(True)
        self.sidebar.itemClicked.connect(self.sidebar_item_clicked)

        self.tabs = QTabWidget()
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.tabs)
        splitter.setStretchFactor(1, 1)

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setAcceptDrops(True)

        self.load_session()

        menu_bar = QMenuBar(self)
        file_menu = menu_bar.addMenu('File')
        open_action = QAction('Open Files', self)
        open_action.triggered.connect(self.open_file_dialog)
        open_folder_action = QAction('Open Folder', self)
        open_folder_action.triggered.connect(self.open_folder_dialog)
        clear_sessions_action = QAction('Clear Sessions', self)
        clear_sessions_action.triggered.connect(self.clear_sessions)
        clear_cache_action = QAction('Clear Cache', self)
        clear_cache_action.triggered.connect(self.clear_cache)
        file_menu.addAction(open_action)
        file_menu.addAction(open_folder_action)
        file_menu.addSeparator()
        file_menu.addAction(clear_sessions_action)
        file_menu.addAction(clear_cache_action)
        self.setMenuBar(menu_bar)

        search_toolbar = self.addToolBar('Search')
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText('Search...')
        search_next_action = QAction('Next', self)
        search_previous_action = QAction('Previous', self)
        search_clear_action = QAction('Clear', self)

        search_next_action.triggered.connect(self.search_next)
        search_previous_action.triggered.connect(self.search_previous)
        search_clear_action.triggered.connect(self.search_clear)

        search_toolbar.addWidget(self.search_field)
        search_toolbar.addAction(search_next_action)
        search_toolbar.addAction(search_previous_action)
        search_toolbar.addAction(search_clear_action)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        self.load_paths(paths)

    def load_paths(self, paths):
        json_files = []
        for path in paths:
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith('.json'):
                            json_files.append(os.path.join(root, file))
            elif os.path.isfile(path) and path.endswith('.json'):
                json_files.append(path)
        self.load_files(json_files)

    def load_files(self, files):
        for file_path in files:
            file_path = os.path.abspath(file_path)
            if file_path not in self.session_files:
                self.session_files.append(file_path)
                self.add_sidebar_item(file_path)
        self.save_session()

    def add_sidebar_item(self, file_path):
        item = QTreeWidgetItem([os.path.basename(file_path)])
        item.setToolTip(0, file_path)
        self.sidebar.addTopLevelItem(item)

    def sidebar_item_clicked(self, item, column):
        file_path = item.toolTip(0)
        self.open_file_in_tab(file_path)
        self.highlight_sidebar_item(file_path)

    def open_file_in_tab(self, file_path):
        for i in range(self.tabs.count()):
            if self.tabs.widget(i).property('file_path') == file_path:
                self.tabs.setCurrentIndex(i)
                return

        cache_file = self.get_cache_file_path(file_path)
        if os.path.exists(cache_file) and os.path.getmtime(cache_file) >= os.path.getmtime(file_path):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                text_widget = QTextBrowser()
                text_widget.setOpenExternalLinks(True)
                text_widget.setStyleSheet("""
                    QTextBrowser {
                        font-family: Arial;
                        font-size: 14px;
                    }
                """)
                text_widget.setHtml(content)
                text_widget.setProperty('file_path', file_path)
                file_name = os.path.basename(file_path)
                self.tabs.addTab(text_widget, file_name)
                self.tabs.setCurrentWidget(text_widget)
            except Exception as e:
                print(f"Error loading cache for {file_path}: {e}")
        else:
            try:
                data = self.read_json_file(file_path)
                if not data:
                    print(f"No valid data found in {file_path}")
                    return
                content = self.process_data(data, file_path)
                try:
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                except Exception as e:
                    print(f"Error writing cache for {file_path}: {e}")
                text_widget = QTextBrowser()
                text_widget.setOpenExternalLinks(True)
                text_widget.setStyleSheet("""
                    QTextBrowser {
                        font-family: Arial;
                        font-size: 14px;
                    }
                """)
                text_widget.setHtml(content)
                text_widget.setProperty('file_path', file_path)
                file_name = os.path.basename(file_path)
                self.tabs.addTab(text_widget, file_name)
                self.tabs.setCurrentWidget(text_widget)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    def get_cache_file_path(self, file_path):
        file_hash = hashlib.md5(file_path.encode('utf-8')).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"{file_hash}.html")
        return cache_file

    def read_json_file(self, file_path):
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
                content = content.encode('utf-8').decode('unicode_escape')

            idx = 0
            content_length = len(content)
            decoder = json.JSONDecoder()

            while idx < content_length:
                try:
                    obj, end_idx = decoder.raw_decode(content, idx)
                    idx = end_idx
                    if isinstance(obj, dict):
                        data.append(obj)
                    elif isinstance(obj, list):
                        data.extend(obj)
                    else:
                        print(f"Skipping non-dictionary JSON object at position {idx} in {file_path}.")
                except json.JSONDecodeError:
                    idx += 1 
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
        return data

    def process_data(self, data, file_path):
        html_content = ""
        url_pattern = re.compile(r'(https?://\S+)')

        for idx, message in enumerate(data):
            try:
                if not isinstance(message, dict):
                    print(f"Skipping item at index {idx} in {file_path}: Not a dictionary.")
                    continue

                author_id = message.get('author', 'Unknown')
                content = message.get('content', '')
                timestamp = message.get('timestamp', '')
                mentions = message.get('mentions', [])
                reactions = message.get('reaction_counts', {})

                if isinstance(timestamp, int):
                    from datetime import datetime
                    timestamp = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

                for mention in mentions:
                    content = content.replace(f"<@{mention}>", f"<b>@{mention}</b>")

                content = url_pattern.sub(r'<a href="\1">\1</a>', content)

                if reactions:
                    reactions_str = ' '.join([f"{emoji}: {count}" for emoji, count in reactions.items()])
                    content += f"<br>Reactions: {reactions_str}"

                html_content += f"""
                <p>
                    <b>{author_id}</b> [{timestamp}]:
                    <br>
                    {content}
                </p>
                <hr>
                """
            except Exception as e:
                print(f"Error processing message at index {idx} in {file_path}: {e}")
                continue

        return html_content

    def highlight_sidebar_item(self, file_path):
        for i in range(self.sidebar.topLevelItemCount()):
            item = self.sidebar.topLevelItem(i)
            if item.toolTip(0) == file_path:
                item.setSelected(True)
            else:
                item.setSelected(False)

    def tab_changed(self, index):
        if index != -1:
            widget = self.tabs.widget(index)
            file_path = widget.property('file_path')
            self.highlight_sidebar_item(file_path)
        else:
            self.highlight_sidebar_item(None)

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)
        self.highlight_sidebar_item(None)

    def save_session(self):
        with open(self.session_file, 'w') as f:
            json.dump(self.session_files, f)

    def load_session(self):
        try:
            with open(self.session_file, 'r') as f:
                self.session_files = json.load(f)
                for file_path in self.session_files:
                    self.add_sidebar_item(file_path)
        except FileNotFoundError:
            pass

    def open_file_dialog(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Open JSON Files",
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options
        )
        if files:
            self.load_files(files)

    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            "",
            QFileDialog.ShowDirsOnly
        )
        if folder:
            self.load_paths([folder])

    def clear_sessions(self):
        confirm = QMessageBox.question(
            self,
            "Clear Sessions",
            "Are you sure you want to clear all sessions? This will remove all files from the sidebar and close all tabs.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.session_files = []
            self.sidebar.clear()
            self.tabs.clear()
            self.save_session()
            self.highlight_sidebar_item(None)

    def clear_cache(self):
        confirm = QMessageBox.question(
            self,
            "Clear Cache",
            "Are you sure you want to clear the cache? This will delete all cached files.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                shutil.rmtree(self.cache_dir)
                os.makedirs(self.cache_dir)
                QMessageBox.information(self, "Clear Cache", "Cache cleared successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Clear Cache", f"Failed to clear cache: {e}")

    def search_next(self):
        query = self.search_field.text()
        if not query:
            return
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, QTextBrowser):
            document = current_widget.document()
            cursor = current_widget.textCursor()
            position = cursor.selectionEnd()
            cursor.setPosition(position)
            found = cursor.find(query)
            if found:
                current_widget.setTextCursor(cursor)
            else:
                cursor.setPosition(0)
                found = cursor.find(query)
                if found:
                    current_widget.setTextCursor(cursor)
                else:
                    QMessageBox.information(self, "Search", "No matches found.")

    def search_previous(self):
        query = self.search_field.text()
        if not query:
            return
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, QTextBrowser):
            document = current_widget.document()
            cursor = current_widget.textCursor()
            position = cursor.selectionStart()
            cursor.setPosition(position)
            found = cursor.find(query, QTextDocument.FindBackward)
            if found:
                current_widget.setTextCursor(cursor)
            else:
                cursor.setPosition(document.characterCount() - 1)
                found = cursor.find(query, QTextDocument.FindBackward)
                if found:
                    current_widget.setTextCursor(cursor)
                else:
                    QMessageBox.information(self, "Search", "No matches found.")

    def search_clear(self):
        self.search_field.clear()
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, QTextBrowser):
            cursor = current_widget.textCursor()
            cursor.clearSelection()
            current_widget.setTextCursor(cursor)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
