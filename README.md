# AI Chatbot with Ultra Enhanced GUI

A modern Python-based chatbot featuring Google Gemini AI integration, natural language understanding, and a sleek PySide6 GUI interface. This project provides an intelligent conversational agent with enhanced visual features, dark/light themes, and professional chat experience.

> **Current Status**: Fully functional with Google Gemini AI, ultra-enhanced GUI, and clean professional codebase.

## Features

- **Ultra Enhanced GUI Interface**
  - Modern PySide6-based interface with animated message bubbles
  - Dark/Light theme switching with smooth transitions
  - Real-time typing indicators and loading animations
  - Connection status monitoring with visual indicators
  - Quick response buttons and categorized suggestions
  - Professional chat experience with message styling

- **Google Gemini AI Integration**
  - Powered by Google's Gemini-1.5-flash model
  - Intelligent responses with context awareness
  - Fallback to rule-based responses when API unavailable
  - Retry mechanism with concurrent processing

- **Natural Language Understanding (NLU)**
  - Intent recognition using spaCy NLP
  - Entity extraction and pattern matching
  - Context-aware conversation handling
  - Support for weather, jokes, time queries, and general chat

- **Memory Management**
  - Persistent conversation history
  - Context retention across sessions
  - Configurable history limits
  - Session management with clear functionality

- **Modular Architecture**
  - Separate Flask backend (port 5003) and GUI frontend
  - Clean, maintainable codebase with natural comments
  - Easy to extend and modify
  - Professional code structure

## What's New

Recent improvements and cleanup:

- **Professional Codebase**: Removed all emojis and AI-generated comments for a clean, professional appearance
- **Enhanced GUI**: Ultra-modern interface with dark/light themes, animations, and visual indicators
- **Google Gemini Integration**: Upgraded to use Google's latest Gemini AI model
- **Code Quality**: Humanized comments and improved code readability
- **Performance**: Optimized backend with retry mechanisms and better error handling

## Requirements

- Python 3.8+
- PySide6 (for the ultra-enhanced GUI)
- Flask (for the backend server)
- Google Generative AI (for Gemini integration)
- spaCy (for natural language understanding)
- Other dependencies listed in `requirements.txt`

## Configuration

1. Create a `.env` file in the project root:
   ```
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   ```

2. Get your Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/suryanshsharma19/ai-chatbot.git
   cd ai-chatbot
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download the spaCy English model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. Set up your Google API key in the `.env` file

## Usage

### Option 1: Using the convenience scripts
1. Start the backend server:
   ```bash
   ./start_backend.sh
   ```

2. In a new terminal, launch the ultra GUI:
   ```bash
   ./start_gui.sh
   ```

### Option 2: Manual startup
1. Start the backend:
   ```bash
   source .venv/bin/activate
   python chatbot.py
   ```

2. In a new terminal, start the GUI:
   ```bash
   source .venv/bin/activate
   python ultra_gui.py
   ```

The backend will run on `http://localhost:5003` and the GUI will connect automatically.

## Project Structure

```
ai-chatbot/
├── ultra_gui.py         # Ultra-enhanced GUI with PySide6
├── chatbot.py           # Flask backend server with Gemini AI
├── memory.py            # Conversation memory management
├── nlu.py              # Natural Language Understanding with spaCy
├── intents.py          # Intent handlers (weather, jokes, time)
├── requirements.txt    # Project dependencies
├── .env                # Environment variables (API keys)
├── chatbot_settings.json # GUI settings and preferences
├── setup.sh            # Project setup script
├── start_backend.sh    # Backend server launcher
└── start_gui.sh        # Ultra GUI launcher
```

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure your PR:
- Includes clear documentation
- Has passing tests (if applicable)
- Follows the project's coding style
- Addresses one of the known issues or adds new features

## Key Components

- **ultra_gui.py**: The main GUI application featuring modern design with animated message bubbles, theme switching, and real-time connection monitoring
- **chatbot.py**: Flask backend server that integrates with Google Gemini AI and provides RESTful API endpoints
- **memory.py**: Manages conversation history and context retention
- **nlu.py**: Processes natural language using spaCy for intent recognition and entity extraction
- **intents.py**: Handles specific intents like weather queries, jokes, and time requests

## Screenshots

The ultra-enhanced GUI features:
- Dark and light theme modes
- Animated message bubbles with smooth transitions
- Real-time typing indicators
- Connection status monitoring
- Quick response buttons organized by categories
- Professional chat interface with modern styling

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Technologies Used

- **PySide6**: Modern GUI framework for the ultra-enhanced interface
- **Google Gemini AI**: Advanced language model for intelligent responses
- **Flask**: Lightweight web framework for the backend API
- **spaCy**: Industrial-strength NLP library for language understanding
- **Python**: Core programming language
- **JSON**: Configuration and settings management

## Acknowledgments

- Google AI for the Gemini language model
- PySide6 for the modern GUI framework
- spaCy for natural language processing capabilities
- Flask for the simple yet powerful backend framework
- Open source community for continuous inspiration

## Contact

For questions and suggestions, please open an issue in the GitHub repository. 
