# AI Chatbot with Natural Language Understanding

A Python-based chatbot with a modern GUI interface, featuring natural language understanding capabilities and persistent memory. This project aims to provide an intelligent conversational agent that can understand and respond to user queries in a natural way.

## Features

- **Natural Language Understanding (NLU)**
  - Intent recognition
  - Entity extraction
  - Context awareness
  - Pattern matching

- **Graphical User Interface**
  - Modern PyQt6-based interface
  - Real-time chat display
  - User-friendly design
  - Customizable themes

- **Memory Management**
  - Persistent conversation history
  - Context retention
  - Session management

- **Modular Architecture**
  - Separate backend and frontend components
  - Easy to extend and modify
  - Well-documented codebase

## Current Status

This project is actively seeking contributions to address several specific challenges:

1. **Intent Recognition Accuracy**
   - Current intent matching algorithm needs improvement
   - Looking for better pattern matching techniques
   - Need help with context understanding

2. **Memory Management**
   - Seeking optimization for large conversation histories
   - Need better context retention mechanisms
   - Looking for efficient storage solutions

3. **GUI Responsiveness**
   - Some UI lag during heavy processing
   - Need better async handling
   - Looking for performance optimization

## Requirements

- Python 3.8+
- PyQt6
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-chatbot.git
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

4. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

## Usage

1. Start the backend server:
   ```bash
   ./start_backend.sh
   ```

2. Launch the GUI:
   ```bash
   ./start_gui.sh
   ```

## Project Structure

```
ai-chatbot/
├── chatbot.py          # Main chatbot logic
├── nlu.py             # Natural Language Understanding module
├── gui.py             # Graphical User Interface
├── memory.py          # Memory management system
├── intents.py         # Intent definitions
├── requirements.txt   # Project dependencies
├── setup.sh           # Setup script
├── start_gui.sh       # GUI launcher
└── start_backend.sh   # Backend launcher
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

## Known Issues

1. **Intent Recognition**
   - Sometimes fails to recognize complex queries
   - Context switching issues
   - Limited pattern matching capabilities

2. **Memory Management**
   - Performance degradation with large conversation histories
   - Context loss in certain scenarios
   - Memory leaks in long sessions

3. **GUI**
   - Occasional UI freezes during processing
   - Memory usage optimization needed
   - Theme switching issues

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- PyQt6 for the GUI framework
- Python's built-in libraries
- Open source community

## Contact

For questions and suggestions, please open an issue in the GitHub repository. 