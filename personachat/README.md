# PersonaChat

A modular AI chat application with FastAPI backend and PyQt6 frontend.

## Features

- Modular plugin architecture
- Secure API key management
- Multiple AI provider support 
- Local chat history storage
- Customizable UI themes
- Cross-platform compatibility

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/personachat.git
   cd personachat
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install requirements:
   ```bash
   pip install -r backend/requirements.txt
   pip install -r frontend/requirements.txt
   ```

4. Configure environment:
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys
   ```

5. Run the application:
   - Start backend:
     ```bash
     python backend/run_server.py
     ```
   - Start frontend (in new terminal):
     ```bash
     python frontend/run_ui.py
     ```

## Development

The project follows a modular architecture:
- `backend/`: FastAPI server with plugins system
- `frontend/`: PyQt6 GUI application
- `backend/plugins_available/`: Directory for user plugins

## License

MIT License - See [LICENSE](LICENSE) for details.