import sys
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QListWidget,
    QLineEdit, QTextEdit, QPushButton, QLabel,
    QHBoxLayout, QVBoxLayout, QMessageBox, QInputDialog
)

FILE = Path("notes.json")


class NotesApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My Notes")
        self.resize(900, 600)

        self.notes = self.load()
        self.current = None
        self.old_title = ""
        self.old_description = ""

        # Notes list
        self.list = QListWidget()
        self.list.itemClicked.connect(self.select_note)

        new_btn = QPushButton("+ New Note")
        new_btn.clicked.connect(self.new_note)

        left = QVBoxLayout()
        left.addWidget(QLabel("NOTES"))
        left.addWidget(self.list)
        left.addWidget(new_btn)

        # Editor
        self.title = QLineEdit()
        self.title.setPlaceholderText("Note title...")

        self.description = QTextEdit()
        self.description.setPlaceholderText("Write your note...")

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_note)

        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.undo)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_note)

        buttons = QHBoxLayout()
        buttons.addWidget(save_btn)
        buttons.addWidget(undo_btn)
        buttons.addWidget(delete_btn)

        right = QVBoxLayout()
        right.addWidget(QLabel("TITLE"))
        right.addWidget(self.title)
        right.addWidget(QLabel("DESCRIPTION"))
        right.addWidget(self.description)
        right.addLayout(buttons)

        # Main layout
        main = QHBoxLayout()
        main.addLayout(left, 1)
        main.addLayout(right, 3)

        widget = QWidget()
        widget.setLayout(main)
        self.setCentralWidget(widget)

        # Style
        self.setStyleSheet("""
            QWidget {
                background: #F4D6DC;
                color: #111111;
                font-size: 14px;
            }

            QLabel {
                color: #111111;
                font-weight: bold;
                padding: 5px;
            }

            QListWidget,
            QLineEdit,
            QTextEdit {
                background: #FFF9FA;
                color: #111111;
                border: 1px solid #C9A227;
                border-radius: 7px;
                padding: 8px;
            }

            QListWidget::item {
                color: #111111;
                padding: 10px;
            }

            QListWidget::item:selected {
                background: #B84A6B;
                color: white;
            }

            QPushButton {
                background: #B84A6B;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 10px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #963B57;
            }
        """)

        self.refresh()

    # Load notes
    def load(self):
        if FILE.exists():
            try:
                return json.loads(
                    FILE.read_text(encoding="utf-8")
                )
            except:
                pass

        return []

    # Save notes to JSON
    def save_file(self):
        FILE.write_text(
            json.dumps(
                self.notes,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

    # Refresh notes list
    def refresh(self):
        self.list.clear()
        self.list.addItems(
            note["title"] for note in self.notes
        )

    # Select note
    def select_note(self, item):
        self.current = self.list.row(item)
        note = self.notes[self.current]

        self.title.setText(note["title"])
        self.description.setPlainText(note["description"])

        self.old_title = note["title"]
        self.old_description = note["description"]

    # Create new note
    def new_note(self):
        title, ok = QInputDialog.getText(
            self,
            "New Note",
            "Title:"
        )

        if not ok or not title.strip():
            return

        title = title.strip()

        self.notes.append({
            "title": title,
            "description": ""
        })

        self.save_file()
        self.refresh()

        self.current = len(self.notes) - 1
        self.list.setCurrentRow(self.current)

        self.title.setText(title)
        self.description.clear()

        self.old_title = title
        self.old_description = ""

    # Save current note
    def save_note(self):
        if self.current is None:
            return

        title = self.title.text().strip()

        if not title:
            return

        self.notes[self.current] = {
            "title": title,
            "description": self.description.toPlainText()
        }

        self.save_file()
        self.refresh()
        self.list.setCurrentRow(self.current)

        self.old_title = title
        self.old_description = self.description.toPlainText()

    # Undo changes
    def undo(self):
        if self.current is not None:
            self.title.setText(self.old_title)
            self.description.setPlainText(
                self.old_description
            )

    # Delete note
    def delete_note(self):
        if self.current is None:
            return

        answer = QMessageBox.question(
            self,
            "Delete",
            "Delete this note?"
        )

        if answer == QMessageBox.Yes:
            self.notes.pop(self.current)
            self.save_file()
            self.refresh()

            self.current = None
            self.title.clear()
            self.description.clear()


app = QApplication(sys.argv)

window = NotesApp()
window.show()

sys.exit(app.exec())