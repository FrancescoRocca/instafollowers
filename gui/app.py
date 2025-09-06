import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QFileDialog,
    QDialog,
    QDialogButtonBox,
    QTextEdit,
)
import json


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("InstaFollowers")
        self.setGeometry(300, 300, 400, 200)
        self.setStyleSheet("""
            QWidget { background-color: #2c3e50; }
            QPushButton { 
                background-color: #3498db; 
                color: white; 
                font-size: 14px; 
                padding: 10px; 
                border: none; 
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #2980b9; }
            QLabel { color: white; font-size: 14px; }
            QTextEdit { 
                background-color: #ecf0f1; 
                color: #2c3e50; 
                padding: 5px; 
                border: 1px solid #bdc3c7; 
                border-radius: 4px;
            }
        """)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.button_followers = QPushButton("Choose Followers JSON")
        self.button_following = QPushButton("Choose Following JSON")
        self.button_calculate = QPushButton("Calculate Difference")
        layout.addWidget(self.button_followers)
        layout.addWidget(self.button_following)
        layout.addWidget(self.button_calculate)

        self.label_selected_followers = QLabel("Followers file: ")
        self.label_selected_following = QLabel("Following file: ")
        layout.addWidget(self.label_selected_followers)
        layout.addWidget(self.label_selected_following)

        self.button_followers.clicked.connect(self.choose_followers_json)
        self.button_following.clicked.connect(self.choose_following_json)
        self.button_calculate.clicked.connect(self.calculate_difference)

        self.followers_data = None
        self.following_data = None

    def choose_followers_json(self):
        filenames, _ = QFileDialog.getOpenFileName(
            self, "Choose Followers JSON", "", "JSON files (*.json)"
        )
        if filenames:
            self.followers_data = read_json(filenames)
            if self.followers_data is None:
                self.label_selected_followers.setText(
                    "Followers file: [Error reading file]"
                )
            else:
                self.label_selected_followers.setText(
                    f"Selected Followers JSON: {filenames}"
                )

    def choose_following_json(self):
        filenames, _ = QFileDialog.getOpenFileName(
            self, "Choose Following JSON", "", "JSON files (*.json)"
        )
        if filenames:
            self.following_data = read_json(filenames)
            if self.following_data is None:
                self.label_selected_following.setText(
                    "Following file: [Error reading file]"
                )
            else:
                self.label_selected_following.setText(
                    f"Selected Following JSON: {filenames}"
                )

    def calculate_difference(self):
        if self.followers_data and self.following_data:
            try:
                diff = difference(self.followers_data, self.following_data)
                self.show_difference_window(diff)
            except Exception as e:
                alert = QMessageBox()
                alert.setWindowTitle("Error")
                alert.setText(f"Error calculating difference: {str(e)}")
                alert.setIcon(QMessageBox.Icon.Critical)
                alert.exec()
        else:
            alert = QMessageBox()
            alert.setWindowTitle("Alert")
            alert.setText("Please select both followers and following JSON files.")
            alert.setIcon(QMessageBox.Icon.Information)
            alert.exec()

    def show_difference_window(self, diff):
        num_names = len(diff)
        self.difference_window = DifferenceWindow(diff, num_names)
        self.difference_window.exec()


class DifferenceWindow(QDialog):
    def __init__(self, diff, num_names):
        super().__init__()
        self.setWindowTitle(f"Difference Result ({num_names} names)")
        self.setGeometry(300, 300, 400, 400)
        self.setStyleSheet("""
            QDialog { background-color: #2c3e50; }
            QLabel { color: white; font-size: 14px; }
            QTextEdit { 
                background-color: #ecf0f1; 
                color: #2c3e50; 
                padding: 5px; 
                border: 1px solid #bdc3c7; 
                border-radius: 4px;
            }
            QDialogButtonBox { padding: 10px; }
        """)
        layout = QVBoxLayout(self)

        label = QLabel("Names in Following but not in Followers:")
        layout.addWidget(label)

        text_edit = QTextEdit()
        text_edit.setPlainText("\n".join(diff))
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)


def read_json(file):
    try:
        with open(file, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("JSON Error")
        msg.setText(f"Failed to read JSON file:\n{str(e)}")
        msg.exec()
        return None


def extract_following(json_data):
    names = set()
    for relationship in json_data.get("relationships_following", []):
        name = relationship["string_list_data"][0]["value"]
        if name:
            names.add(name)
    return names


def extract_followers(json_data):
    names = set()
    for follower in json_data:
        name = follower["string_list_data"][0]["value"]
        if name:
            names.add(name)
    return names


def difference(json1, json2):
    set1 = extract_followers(json1)
    set2 = extract_following(json2)
    diff = set2 - set1
    return diff


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
