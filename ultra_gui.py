import sys
import requests
import threading
import json
import os
import re
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QScrollArea, 
    QLabel, QFrame, QSplitter, QMenuBar, QMenu, QStatusBar,
    QComboBox, QCheckBox, QSlider, QTabWidget, QTextBrowser,
    QFileDialog, QDialog, QDialogButtonBox, QFormLayout, QSpinBox,
    QSystemTrayIcon, QStyle, QProgressBar, QToolBar,
    QSizePolicy, QGridLayout, QButtonGroup, QRadioButton
)
from PySide6.QtCore import Qt, Signal, QObject, QThread, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QFont, QPixmap, QIcon, QAction, QPalette, QColor, QTextCursor, QKeySequence, QShortcut

CHATBOT_API_URL = "http://127.0.0.1:5003/chat"

# Enhanced color scheme with more variants
class Colors:
    # Light theme
    LIGHT_PRIMARY = "#007acc"
    LIGHT_BG = "#ffffff"
    LIGHT_SURFACE = "#f8f9fa"
    LIGHT_CARD = "#ffffff"
    LIGHT_TEXT = "#212529"
    LIGHT_TEXT_SECONDARY = "#6c757d"
    LIGHT_BORDER = "#dee2e6"
    
    # Dark theme
    DARK_PRIMARY = "#0078d4"
    DARK_BG = "#1e1e1e"
    DARK_SURFACE = "#2d2d30"
    DARK_CARD = "#3c3c3c"
    DARK_TEXT = "#ffffff"
    DARK_TEXT_SECONDARY = "#cccccc"
    DARK_BORDER = "#404040"
    
    # Message bubbles
    USER_BUBBLE_LIGHT = "#007acc"
    USER_BUBBLE_DARK = "#0078d4"
    BOT_BUBBLE_LIGHT = "#28a745"
    BOT_BUBBLE_DARK = "#238636"
    
    # Status colors
    SUCCESS = "#28a745"
    ERROR = "#dc3545"
    WARNING = "#ffc107"
    INFO = "#17a2b8"

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)
    result = Signal(str, str)
    typing = Signal(bool)
    progress = Signal(int)

class ChatbotWorker(QObject):
    def __init__(self, message):
        super().__init__()
        self.signals = WorkerSignals()
        self.user_message = message
        self._is_running = True

    def run(self):
        if not self._is_running:
            return

        try:
            # Emit typing indicator and progress
            self.signals.typing.emit(True)
            self.signals.progress.emit(25)
            
            response = requests.post(CHATBOT_API_URL, json={"message": self.user_message}, timeout=30)
            self.signals.progress.emit(75)
            
            response.raise_for_status()
            self.signals.progress.emit(90)

            data = response.json()
            bot_reply = data.get("reply", "Sorry, I received an unexpected response.")
            
            if self._is_running:
                self.signals.progress.emit(100)
                self.signals.result.emit(bot_reply, "chatbot")

        except requests.exceptions.Timeout:
            error_msg = "⏰ Request timed out. The server might be busy."
            if self._is_running: 
                self.signals.error.emit(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "Cannot connect to chatbot server. Please ensure it's running on port 5003."
            if self._is_running: 
                self.signals.error.emit(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            if self._is_running: 
                self.signals.error.emit(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            if self._is_running: 
                self.signals.error.emit(error_msg)
        finally:
            self.signals.typing.emit(False)
            self.signals.progress.emit(0)
            if self._is_running:
                self.signals.finished.emit()

    def stop(self):
        self._is_running = False

class AnimatedMessageBubble(QFrame):
    def __init__(self, sender, message, timestamp, is_user=False, is_error=False):
        super().__init__()
        self.setFrameStyle(QFrame.NoFrame)
        self.message_text = message
        
        # Animation setup
        self.opacity_effect = None
        self.setup_animation()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        # Message content with rich text support
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        self.content_label.setFont(QFont("Segoe UI", 11))
        self.content_label.setOpenExternalLinks(True)
        
        # Process message for links, formatting, etc.
        processed_message = self.process_message(message)
        self.content_label.setText(processed_message)
        
        # Metadata (sender and timestamp)
        meta_label = QLabel(f"{sender} • {timestamp}")
        meta_label.setFont(QFont("Segoe UI", 9))
        meta_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        # Styling with improved contrast
        if is_error:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {Colors.ERROR};
                    border-radius: 15px;
                    margin: 3px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                QLabel {{ 
                    color: white; 
                    font-weight: 500;
                }}
            """)
        elif is_user:
            self.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {Colors.USER_BUBBLE_LIGHT}, stop:1 #0056b3);
                    border-radius: 15px;
                    margin: 3px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                QLabel {{ 
                    color: white; 
                    font-weight: 500;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {Colors.BOT_BUBBLE_LIGHT}, stop:1 #1e7e34);
                    border-radius: 15px;
                    margin: 3px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                QLabel {{ 
                    color: white; 
                    font-weight: 500;
                }}
            """)
        
        layout.addWidget(self.content_label)
        layout.addWidget(meta_label)
        self.setLayout(layout)
        
        # Animate in
        self.animate_in()
    
    def process_message(self, message):
        # Handle special formatting in messages like links and expressions
        # Convert URLs to clickable links
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        message = re.sub(url_pattern, r'<a href="\g<0>">\g<0></a>', message)
        
        # Convert newlines to HTML breaks
        message = message.replace('\n', '<br>')
        
        # Bold text with **text**
        message = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', message)
        
        # Italic text with *text*
        message = re.sub(r'\*(.*?)\*', r'<i>\1</i>', message)
        
        return message
    
    def setup_animation(self):
        # Initialize the fade-in animation for message bubbles
        pass
    
    def animate_in(self):
        # Start the fade-in animation when a new message appears
        # Start with 0 opacity and animate to full
        self.setStyleSheet(self.styleSheet() + "QFrame { opacity: 0; }")
        
        # Simple fade-in effect using timer
        self.opacity = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.fade_step)
        self.timer.start(30)  # 30ms intervals
    
    def fade_step(self):
        # Update opacity during animation
        self.opacity += 0.1
        if self.opacity >= 1:
            self.opacity = 1
            self.timer.stop()
        
        # Update stylesheet with opacity
        current_style = self.styleSheet()
        # Remove old opacity and add new one
        current_style = re.sub(r'opacity: [0-9.]+;', '', current_style)
        self.setStyleSheet(current_style + f"QFrame {{ opacity: {self.opacity}; }}")

class EmojiPanel(QWidget):
    emoji_selected = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QGridLayout()
        layout.setSpacing(5)
        
        # Common text expressions
        emojis = [
            ":)", ":(", ":D", ":P", ";)", ":o", ":|", ":/",
            ":*", "<3", "</3", ":@", "8)", "B)", ":-)", ":-(",
            ":-D", ":-P", ";-)", ":-o", ":-|", ":-/", ":-*", "^_^",
            ">:(", ":-(", "xD", "=)", "=(", "=D", "=P", ";="
        ]
        
        row = 0
        col = 0
        for emoji in emojis:
            btn = QPushButton(emoji)
            btn.setFixedSize(35, 35)
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #404040;
                    border-radius: 5px;
                    font-size: 12px;
                    background-color: #3c3c3c;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                    border-color: #007acc;
                }
            """)
            btn.clicked.connect(lambda checked, e=emoji: self.emoji_selected.emit(e))
            
            layout.addWidget(btn, row, col)
            col += 1
            if col >= 8:
                col = 0
                row += 1
        
        self.setLayout(layout)
        self.setMaximumHeight(200)

class AdvancedQuickResponseWidget(QWidget):
    response_clicked = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)
        
        # Category buttons
        categories_layout = QHBoxLayout()
        self.category_buttons = QButtonGroup()
        
        categories = [
            ("General", ["Hello", "Help", "Thank you", "Goodbye"]),
            ("Questions", ["What time?", "Weather?", "News?", "Advice?"]),
            ("Fun", ["Tell joke", "Sing song", "Play game", "Surprise me"]),
            ("Tasks", ["To-do list", "Take notes", "Set reminder", "Search"])
        ]
        
        self.response_widgets = {}
        
        for i, (category, responses) in enumerate(categories):
            radio = QRadioButton(category)
            if i == 0:
                radio.setChecked(True)
            radio.toggled.connect(lambda checked, cat=category: self.show_category(cat) if checked else None)
            categories_layout.addWidget(radio)
            self.category_buttons.addButton(radio)
            
            # Create response buttons for this category
            response_widget = QWidget()
            response_layout = QHBoxLayout(response_widget)
            response_layout.setContentsMargins(0, 0, 0, 0)
            
            for response in responses:
                btn = QPushButton(response)
                btn.setStyleSheet("""
                    QPushButton {
                        border: 1px solid #007acc;
                        border-radius: 15px;
                        padding: 6px 12px;
                        background-color: rgba(0, 122, 204, 0.1);
                        color: #007acc;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: rgba(0, 122, 204, 0.2);
                    }
                    QPushButton:pressed {
                        background-color: rgba(0, 122, 204, 0.3);
                    }
                """)
                btn.clicked.connect(lambda checked, text=response: self.response_clicked.emit(text.split(' ', 1)[-1]))
                response_layout.addWidget(btn)
            
            response_layout.addStretch()
            self.response_widgets[category] = response_widget
            
            if i == 0:
                response_widget.show()
            else:
                response_widget.hide()
        
        categories_layout.addStretch()
        layout.addLayout(categories_layout)
        
        # Add all response widgets
        for widget in self.response_widgets.values():
            layout.addWidget(widget)
        
        self.setLayout(layout)
    
    def show_category(self, category):
        # Display quick response options based on selected category
        for cat, widget in self.response_widgets.items():
            if cat == category:
                widget.show()
            else:
                widget.hide()

class EnhancedTypingIndicator(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("AI is thinking")
        self.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-style: italic;
                padding: 8px 15px;
                background-color: rgba(108, 117, 125, 0.1);
                border-radius: 10px;
                margin: 5px;
            }
        """)
        self.hide()
        
        # Advanced animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_dots)
        self.dot_count = 0
        self.thinking_states = ["thinking", "processing", "analyzing", "generating"]
        self.state_index = 0
        
    def show_typing(self):
        self.show()
        self.timer.start(800)
        
    def hide_typing(self):
        self.hide()
        self.timer.stop()
        
    def animate_dots(self):
        self.dot_count = (self.dot_count + 1) % 4
        dots = "." * self.dot_count
        
        # Occasionally change the thinking state
        if self.dot_count == 0:
            self.state_index = (self.state_index + 1) % len(self.thinking_states)
            state = self.thinking_states[self.state_index]
            self.setText(f"AI is {state}{dots}")
        else:
            current_text = self.text().split('.')[0]
            self.setText(f"{current_text}{dots}")

class ConnectionStatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.check_connection()
        
        # Auto-check connection every 10 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connection)
        self.timer.start(10000)
        
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        self.status_dot = QLabel("●")
        self.status_dot.setFont(QFont("Segoe UI", 12))
        
        self.status_text = QLabel("Checking...")
        self.status_text.setFont(QFont("Segoe UI", 9))
        
        layout.addWidget(self.status_dot)
        layout.addWidget(self.status_text)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def check_connection(self):
        # Check if backend server is running
        try:
            response = requests.get("http://127.0.0.1:5003/", timeout=2)
            if response.status_code == 200:
                self.set_status("connected")
            else:
                self.set_status("error")
        except:
            self.set_status("disconnected")
    
    def set_status(self, status):
        # Update the connection status indicator
        if status == "connected":
            self.status_dot.setStyleSheet("color: #28a745;")
            self.status_text.setText("Connected")
            self.status_text.setStyleSheet("color: #28a745;")
        elif status == "disconnected":
            self.status_dot.setStyleSheet("color: #dc3545;")
            self.status_text.setText("Disconnected")
            self.status_text.setStyleSheet("color: #dc3545;")
        elif status == "error":
            self.status_dot.setStyleSheet("color: #ffc107;")
            self.status_text.setText("Error")
            self.status_text.setStyleSheet("color: #ffc107;")

class UltraEnhancedChatbotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = "Dark"
        self.conversation_history = []
        self.settings = self.load_settings()
        self.init_ui()
        self.setup_shortcuts()
        self.apply_theme()
        
    def load_settings(self):
        # Load user preferences from file
        settings_file = "chatbot_settings.json"
        default_settings = {
            "theme": "Light",
            "font_size": 12,
            "auto_scroll": True,
            "sound_effects": False,
            "animations": True,
            "save_on_exit": True
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return {**default_settings, **settings}
        except:
            pass
        
        return default_settings
    
    def save_settings(self):
        # Save current settings to file
        try:
            with open("chatbot_settings.json", 'w') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass
        
    def init_ui(self):
        self.setWindowTitle("AI Chatbot - Ultra Enhanced")
        self.setGeometry(100, 100, 1000, 800)
        self.setMinimumSize(800, 600)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Top status bar
        status_layout = QHBoxLayout()
        
        self.connection_status = ConnectionStatusWidget()
        status_layout.addWidget(self.connection_status)
        
        status_layout.addStretch()
        
        # Theme toggle with animation
        self.theme_btn = QPushButton("Dark Mode")
        self.theme_btn.clicked.connect(self.toggle_theme)
        status_layout.addWidget(self.theme_btn)
        
        main_layout.addLayout(status_layout)
        
        # Progress bar for requests
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 10px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 9px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # Chat area with enhanced scroll
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #404040;
                border-radius: 10px;
                background-color: #2d2d30;
            }
            QScrollBar::vertical {
                background: #404040;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #666666;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #888888;
            }
        """)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        
        self.chat_scroll.setWidget(self.chat_widget)
        main_layout.addWidget(self.chat_scroll)
        
        # Typing indicator
        self.typing_indicator = EnhancedTypingIndicator()
        main_layout.addWidget(self.typing_indicator)
        
        # Enhanced input area
        input_container = QFrame()
        input_container.setFrameStyle(QFrame.StyledPanel)
        input_container.setStyleSheet("""
            QFrame {
                background-color: #3c3c3c;
                border: 1px solid #404040;
                border-radius: 15px;
                padding: 5px;
            }
        """)
        
        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(8)
        
        # Main input row
        main_input_layout = QHBoxLayout()
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type your message here... (Press Enter to send)")
        self.user_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #404040;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 13px;
                background-color: #2d2d30;
                color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #007acc;
                background-color: #333333;
            }
            QLineEdit::placeholder {
                color: #cccccc;
            }
        """)
        self.user_input.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007acc, stop:1 #0056b3);
                color: white;
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0056b3, stop:1 #004494);
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        
        main_input_layout.addWidget(self.user_input)
        main_input_layout.addWidget(self.send_button)
        
        input_layout.addLayout(main_input_layout)
        
        # Quick responses
        self.quick_responses = AdvancedQuickResponseWidget()
        self.quick_responses.response_clicked.connect(self.send_quick_response)
        input_layout.addWidget(self.quick_responses)
        
        # Emoji panel (initially hidden)
        self.emoji_panel = EmojiPanel()
        self.emoji_panel.emoji_selected.connect(self.insert_emoji)
        self.emoji_panel.hide()
        input_layout.addWidget(self.emoji_panel)
        
        main_layout.addWidget(input_container)
        
        # Bottom controls
        bottom_layout = QHBoxLayout()
        
        # Action buttons with icons
        self.clear_btn = QPushButton("Clear")
        self.save_btn = QPushButton("Save")
        self.load_btn = QPushButton("Load")
        self.export_btn = QPushButton("Export")
        
        for btn in [self.clear_btn, self.save_btn, self.load_btn, self.export_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3c3c3c;
                    border: 1px solid #404040;
                    border-radius: 8px;
                    padding: 8px 15px;
                    font-size: 11px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                    border-color: #007acc;
                }
                QPushButton:pressed {
                    background-color: #2a2a2a;
                }
            """)
        
        self.clear_btn.clicked.connect(self.clear_chat)
        self.save_btn.clicked.connect(self.save_conversation)
        self.load_btn.clicked.connect(self.load_conversation)
        self.export_btn.clicked.connect(self.export_conversation)
        
        bottom_layout.addWidget(self.clear_btn)
        bottom_layout.addWidget(self.save_btn)
        bottom_layout.addWidget(self.load_btn)
        bottom_layout.addWidget(self.export_btn)
        bottom_layout.addStretch()
        
        # Statistics
        self.stats_label = QLabel("Messages: 0 | Session: 0m")
        self.stats_label.setStyleSheet("color: #6c757d; font-size: 10px;")
        bottom_layout.addWidget(self.stats_label)
        
        main_layout.addLayout(bottom_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ultra Enhanced Chatbot Ready!")
        
        # Initialize variables
        self.thread = None
        self.worker = None
        self.message_count = 0
        self.session_start = datetime.now()
        self.emoji_panel_visible = False
        
        # Welcome message
        self.add_message("Ultra AI", "Welcome to the Ultra Enhanced AI Chatbot!\n\nI'm equipped with:\n• Beautiful message bubbles\n• Dark/Light themes\n• Quick responses\n• Expression support\n• Connection monitoring\n• And much more!\n\nHow can I assist you today?", False)
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        new_action = QAction('&New Chat', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.clear_chat)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        save_action = QAction('&Save Chat', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_conversation)
        file_menu.addAction(save_action)
        
        load_action = QAction('&Load Chat', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_conversation)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        
        theme_action = QAction('Toggle &Theme', self)
        theme_action.setShortcut('Ctrl+T')
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create application toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Quick action buttons
        new_action = QAction('New', self)
        new_action.setToolTip('New Chat (Ctrl+N)')
        new_action.triggered.connect(self.clear_chat)
        toolbar.addAction(new_action)
        
        save_action = QAction('Save', self)
        save_action.setToolTip('Save Chat (Ctrl+S)')
        save_action.triggered.connect(self.save_conversation)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        theme_action = QAction('Theme', self)
        theme_action.setToolTip('Toggle Theme (Ctrl+T)')
        theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(theme_action)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        shortcuts = [
            ('Ctrl+Return', self.send_message),
            ('Ctrl+L', self.clear_chat),
            ('Ctrl+E', self.toggle_emoji_panel),
            ('F11', self.toggle_fullscreen)
        ]
        
        for key, func in shortcuts:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(func)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def toggle_emoji_panel(self):
        """Toggle emoji panel visibility"""
        self.emoji_panel_visible = not self.emoji_panel_visible
        if self.emoji_panel_visible:
            self.emoji_panel.show()
            self.emoji_btn.setText("⬇️")
        else:
            self.emoji_panel.hide()
            self.emoji_btn.setText("☺")
    
    def insert_emoji(self, emoji):
        """Insert emoji into input field"""
        current_text = self.user_input.text()
        cursor_pos = self.user_input.cursorPosition()
        new_text = current_text[:cursor_pos] + emoji + current_text[cursor_pos:]
        self.user_input.setText(new_text)
        self.user_input.setCursorPosition(cursor_pos + len(emoji))
        self.user_input.setFocus()
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.current_theme == "Light":
            self.current_theme = "Dark"
            self.theme_btn.setText("Light Mode")
        else:
            self.current_theme = "Light"
            self.theme_btn.setText("Dark Mode")
        
        self.settings["theme"] = self.current_theme
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme"""
        if self.current_theme == "Dark":
            # Dark theme styles
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {Colors.DARK_BG};
                    color: {Colors.DARK_TEXT};
                }}
                QMenuBar {{
                    background-color: {Colors.DARK_SURFACE};
                    color: {Colors.DARK_TEXT};
                    border-bottom: 1px solid {Colors.DARK_BORDER};
                }}
                QMenuBar::item {{
                    background-color: transparent;
                    padding: 4px 8px;
                }}
                QMenuBar::item:selected {{
                    background-color: {Colors.DARK_PRIMARY};
                }}
                QScrollArea {{
                    background-color: {Colors.DARK_SURFACE};
                    border: 1px solid {Colors.DARK_BORDER};
                }}
                QFrame {{
                    background-color: {Colors.DARK_CARD};
                    border: 1px solid {Colors.DARK_BORDER};
                }}
            """)
        else:
            # Light theme styles
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {Colors.LIGHT_BG};
                    color: {Colors.LIGHT_TEXT};
                }}
                QMenuBar {{
                    background-color: {Colors.LIGHT_SURFACE};
                    color: {Colors.LIGHT_TEXT};
                    border-bottom: 1px solid {Colors.LIGHT_BORDER};
                }}
                QMenuBar::item {{
                    background-color: transparent;
                    padding: 4px 8px;
                }}
                QMenuBar::item:selected {{
                    background-color: {Colors.LIGHT_PRIMARY};
                    color: white;
                }}
                QScrollArea {{
                    background-color: {Colors.LIGHT_SURFACE};
                    border: 1px solid {Colors.LIGHT_BORDER};
                }}
            """)
    
    def add_message(self, sender, message, is_user, is_error=False):
        """Add a message to the chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create animated message bubble
        bubble = AnimatedMessageBubble(sender, message, timestamp, is_user, is_error)
        
        # Create container for proper alignment
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        if is_user:
            container_layout.addStretch()
            container_layout.addWidget(bubble, 0)
        else:
            container_layout.addWidget(bubble, 0)
            container_layout.addStretch()
        
        self.chat_layout.addWidget(container)
        
        # Update statistics
        self.message_count += 1
        session_time = (datetime.now() - self.session_start).total_seconds() // 60
        self.stats_label.setText(f"Messages: {self.message_count} | Session: {int(session_time)}m")
        
        # Store in history
        self.conversation_history.append({
            "sender": sender,
            "message": message,
            "timestamp": timestamp,
            "is_user": is_user,
            "is_error": is_error
        })
        
        # Auto-scroll to bottom
        if self.settings.get("auto_scroll", True):
            QTimer.singleShot(100, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """Scroll chat to bottom"""
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        """Send a message to the chatbot"""
        user_message = self.user_input.text().strip()
        if not user_message:
            return
        
        self.add_message("You", user_message, True)
        self.user_input.clear()
        
        self.set_input_enabled(False)
        self.progress_bar.show()
        self.status_bar.showMessage("Processing your message...")
        
        # Start worker thread
        self.thread = QThread()
        self.worker = ChatbotWorker(user_message)
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.worker.signals.result.connect(self.handle_bot_reply)
        self.worker.signals.error.connect(self.handle_error)
        self.worker.signals.typing.connect(self.handle_typing)
        self.worker.signals.progress.connect(self.progress_bar.setValue)
        self.worker.signals.finished.connect(self.thread.quit)
        self.worker.signals.finished.connect(self.worker.deleteLater)
        self.worker.signals.finished.connect(self.thread.deleteLater)
        self.worker.signals.finished.connect(lambda: self.set_input_enabled(True))
        self.worker.signals.finished.connect(lambda: self.progress_bar.hide())
        self.worker.signals.finished.connect(lambda: self.status_bar.showMessage("Ready for your next message!"))
        
        self.thread.started.connect(self.worker.run)
        self.thread.start()
    
    def send_quick_response(self, message):
        """Send a quick response"""
        self.user_input.setText(message)
        self.send_message()
    
    def handle_bot_reply(self, reply, tag):
        """Handle bot reply"""
        self.add_message("Ultra AI", reply, False)
    
    def handle_error(self, error_message):
        """Handle error messages"""
        self.add_message("System", error_message, False, True)
    
    def handle_typing(self, is_typing):
        """Handle typing indicator"""
        if is_typing:
            self.typing_indicator.show_typing()
        else:
            self.typing_indicator.hide_typing()
    
    def set_input_enabled(self, enabled):
        # Enable or disable input controls
        self.user_input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        
        if enabled:
            self.user_input.setFocus()
    
    def clear_chat(self):
        """Clear all messages"""
        # Remove all message widgets
        for i in reversed(range(self.chat_layout.count())):
            child = self.chat_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        self.conversation_history.clear()
        self.message_count = 0
        self.session_start = datetime.now()
        self.stats_label.setText("Messages: 0 | Session: 0m")
        
        # Add welcome message
        self.add_message("Ultra AI", "Chat cleared! Ready for a fresh conversation. How can I help you?", False)
    
    def save_conversation(self):
        """Save conversation to file"""
        if not self.conversation_history:
            QMessageBox.information(self, "Save Chat", "No conversation to save!")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Conversation", 
            f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                conversation_data = {
                    "metadata": {
                        "saved_at": datetime.now().isoformat(),
                        "message_count": len(self.conversation_history),
                        "session_duration": str(datetime.now() - self.session_start)
                    },
                    "messages": self.conversation_history
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(conversation_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "Save Chat", f"Conversation saved successfully!\n{filename}")
                self.status_bar.showMessage(f"Saved: {os.path.basename(filename)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save conversation:\n{str(e)}")
    
    def load_conversation(self):
        """Load conversation from file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Conversation", "", "JSON Files (*.json)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Clear current chat
                self.clear_chat()
                
                # Load messages
                messages = data.get("messages", data) if "messages" in data else data
                
                for msg in messages:
                    self.add_message(
                        msg['sender'],
                        msg['message'],
                        msg['is_user'],
                        msg.get('is_error', False)
                    )
                
                metadata = data.get("metadata", {})
                msg_count = metadata.get("message_count", len(messages))
                
                QMessageBox.information(
                    self, "Load Chat", 
                    f"Conversation loaded successfully!\n\n"
                    f"Messages: {msg_count}\n"
                    f"File: {os.path.basename(filename)}"
                )
                self.status_bar.showMessage(f"Loaded: {os.path.basename(filename)}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load conversation:\n{str(e)}")
    
    def export_conversation(self):
        """Export conversation as text"""
        if not self.conversation_history:
            QMessageBox.information(self, "Export Chat", "No conversation to export!")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Conversation",
            f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=" * 50 + "\n")
                    f.write("AI CHATBOT CONVERSATION EXPORT\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Messages: {len(self.conversation_history)}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for msg in self.conversation_history:
                        timestamp = msg['timestamp']
                        sender = msg['sender']
                        message = msg['message']
                        
                        f.write(f"[{timestamp}] {sender}:\n")
                        f.write(f"{message}\n\n")
                
                QMessageBox.information(self, "Export Chat", f"Conversation exported successfully!\n{filename}")
                self.status_bar.showMessage(f"Exported: {os.path.basename(filename)}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export conversation:\n{str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About Ultra Enhanced Chatbot",
            """
            <h2>Ultra Enhanced AI Chatbot</h2>
            <p><b>Version:</b> 2.0</p>
            <p><b>Features:</b></p>
            <ul>
                <li>Beautiful animated message bubbles</li>
                <li>Dark & Light themes</li>
                <li>Emoji support with picker</li>
                <li>Quick response categories</li>
                <li>Advanced typing indicators</li>
                <li>Connection status monitoring</li>
                <li>Save/Load conversations</li>
                <li>Export to text</li>
                <li>Keyboard shortcuts</li>
                <li>Session statistics</li>
                <li>And much more!</li>
            </ul>
            <p><b>Built with:</b> Python & PySide6</p>
            <p>Enjoy chatting!</p>
            """
        )
    
    def closeEvent(self, event):
        """Handle application close"""
        # Save settings
        self.save_settings()
        
        # Stop worker if running
        if self.thread and self.thread.isRunning():
            if self.worker:
                self.worker.stop()
            self.thread.quit()
            self.thread.wait(1000)
        
        # Ask to save conversation if enabled
        if (self.settings.get("save_on_exit", True) and 
            self.conversation_history and 
            len(self.conversation_history) > 1):  # More than just welcome message
            
            reply = QMessageBox.question(
                self, "Save Conversation?",
                "Would you like to save the current conversation before closing?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Yes:
                self.save_conversation()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Ultra Enhanced AI Chatbot")
    app.setOrganizationName("ChatBot Ultra")
    app.setApplicationVersion("2.0")
    
    # Set high DPI support
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
    window = UltraEnhancedChatbotGUI()
    window.show()
    
    sys.exit(app.exec())