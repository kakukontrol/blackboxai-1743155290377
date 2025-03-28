from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTabWidget
)
from PyQt6.QtCore import Qt
from frontend.app.api_client import ApiClient

class SettingsDialog(QDialog):
    def __init__(self, api_client: ApiClient, current_settings: dict):
        super().__init__()
        self.api_client = api_client
        self.current_settings = current_settings
        
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 300)
        
        self.tabs = QTabWidget()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.tabs)
        
        # API Keys Tab
        api_keys_tab = QWidget()
        api_keys_layout = QFormLayout()
        self.groq_key_input = QLineEdit()
        self.groq_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.openrouter_key_input = QLineEdit()
        self.openrouter_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        api_keys_layout.addRow(QLabel("Groq API Key:"), self.groq_key_input)
        api_keys_layout.addRow(QLabel("OpenRouter API Key:"), self.openrouter_key_input)
        api_keys_tab.setLayout(api_keys_layout)
        self.tabs.addTab(api_keys_tab, "API Keys")
        
        # General Tab
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.provider_combo = QComboBox()
        self.model_combo = QComboBox()
        
        general_layout.addWidget(QLabel("Theme:"))
        general_layout.addWidget(self.theme_combo)
        general_layout.addWidget(QLabel("Default Provider:"))
        general_layout.addWidget(self.provider_combo)
        general_layout.addWidget(QLabel("Default Model:"))
        general_layout.addWidget(self.model_combo)
        general_tab.setLayout(general_layout)
        self.tabs.addTab(general_tab, "General")
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        self.layout().addLayout(button_layout)
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        self.load_settings()

    def load_settings(self):
        """Load current settings into the dialog."""
        self.groq_key_input.setText(self.current_settings.get("api_keys", {}).get("groq", ""))
        self.openrouter_key_input.setText(self.current_settings.get("api_keys", {}).get("openrouter", ""))
        self.theme_combo.setCurrentText(self.current_settings.get("theme", "Light"))
        self.provider_combo.setCurrentText(self.current_settings.get("default_provider", "groq"))
        self.model_combo.setCurrentText(self.current_settings.get("default_model", "llama3-8b-8192"))

    def get_settings(self) -> dict:
        """Collect settings from the dialog."""
        return {
            "api_keys": {
                "groq": self.groq_key_input.text(),
                "openrouter": self.openrouter_key_input.text()
            },
            "theme": self.theme_combo.currentText(),
            "default_provider": self.provider_combo.currentText(),
            "default_model": self.model_combo.currentText()
        }