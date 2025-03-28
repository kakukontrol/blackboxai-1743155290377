from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal

class ChatWidget(QWidget):
    """Widget for chat interface."""
    
    settings_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)
        
        self.input_field = QTextEdit()
        self.layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)
        
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.request_settings)
        self.layout.addWidget(self.settings_button)
        
    def send_message(self):
        """Send message to chat."""
        message = self.input_field.toPlainText()
        if message:
            self.chat_display.append(f"You: {message}")
            self.input_field.clear()
            # Here you would typically send the message to the backend
            
    def request_settings(self):
        """Request to open settings."""
        self.settings_requested.emit()