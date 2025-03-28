from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton

class SettingsWidget(QWidget):
    """Widget for application settings."""
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        # API Key Section
        self.api_key_label = QLabel("API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your API key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        
        self.layout.addWidget(self.api_key_label)
        self.layout.addWidget(self.api_key_input)
        self.layout.addWidget(self.save_button)
        
    def save_settings(self):
        """Save settings to configuration."""
        api_key = self.api_key_input.text()
        if api_key:
            # Here you would typically save the settings to backend
            print(f"API Key saved: {api_key[:4]}...")  # Don't print full key