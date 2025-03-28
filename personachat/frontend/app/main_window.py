from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QComboBox,
    QMenuBar, QMenu, QLabel
)
from PyQt6.QtCore import Qt
from .api_client import ApiClient
from .dialogs.settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_client = ApiClient()
        self.settings = self.api_client.get_settings()
        
        # Main window setup
        self.setWindowTitle("PersonaChat")
        self.resize(800, 600)
        
        # Create menu bar
        menubar = QMenuBar()
        settings_menu = QMenu("Settings", self)
        settings_action = settings_menu.addAction("Open Settings")
        settings_action.triggered.connect(self.open_settings_dialog)
        menubar.addMenu(settings_menu)
        self.setMenuBar(menubar)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        
        # Provider/model selection
        control_layout = QHBoxLayout()
        self.provider_combo = QComboBox()
        self.model_combo = QComboBox()
        self.update_provider_model_combos()
        control_layout.addWidget(QLabel("Provider:"))
        control_layout.addWidget(self.provider_combo)
        control_layout.addWidget(QLabel("Model:"))
        control_layout.addWidget(self.model_combo)
        layout.addLayout(control_layout)
        
        # User input field
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type your message here...")
        layout.addWidget(self.user_input)
        
        # Send button
        self.send_button = QPushButton("Send")
        layout.addWidget(self.send_button)
        
        # Connect signals
        self.send_button.clicked.connect(self.handle_send_button)
        self.user_input.returnPressed.connect(self.handle_send_button)
        self.provider_combo.currentTextChanged.connect(self.update_models_combo)

    def update_provider_model_combos(self):
        """Update provider and model dropdowns from settings"""
        providers = self.api_client.get_providers()
        self.provider_combo.clear()
        self.provider_combo.addItems(providers)
        
        if self.settings.get("default_provider"):
            self.provider_combo.setCurrentText(self.settings["default_provider"])
        self.update_models_combo()

    def update_models_combo(self):
        """Update models dropdown based on selected provider"""
        provider = self.provider_combo.currentText()
        models = self.api_client.get_models(provider)
        self.model_combo.clear()
        self.model_combo.addItems(models)
        
        if self.settings.get("default_model"):
            self.model_combo.setCurrentText(self.settings["default_model"])

    def open_settings_dialog(self):
        """Open and handle settings dialog"""
        dialog = SettingsDialog(self.api_client, self.settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_settings = dialog.get_settings()
            if self.api_client.save_settings(new_settings):
                self.settings = new_settings
                self.update_provider_model_combos()

    def handle_send_button(self):
        """Handle the send button click event."""
        message = self.user_input.text()
        if not message:
            return
        
        # Append user's message to chat display
        self.chat_display.append(f"You: {message}")
        self.user_input.clear()
        
        # Get selected provider and model
        provider = self.provider_combo.currentText()
        model = self.model_combo.currentText()
        
        # Send message to backend
        response = self.api_client.send_message(message, provider, model)
        if response:
            self.chat_display.append(f"AI: {response}")
        else:
            self.chat_display.append("Error: Unable to get response from AI.")