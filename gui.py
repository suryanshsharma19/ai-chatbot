import sys
import requests
import threading
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QObject, QThread

CHATBOT_API_URL = "http://127.0.0.1:5000/chat"
USER_COLOR = "blue"
BOT_COLOR = "green"
ERROR_COLOR = "red"
INFO_COLOR = "gray"

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)
    result = Signal(str, str)

class ChatbotWorker(QObject):
    def __init__(self, message):
        super().__init__()
        self.signals = WorkerSignals()
        self.user_message = message
        self._is_running = True

    def run(self):
        print("WORKER: Thread started.")
        if not self._is_running:
            print("WORKER: Not running flag set, exiting.")
            return

        try:
            print(f"WORKER: Making POST request to {CHATBOT_API_URL}...")
            response = requests.post(CHATBOT_API_URL, json={"message": self.user_message}, timeout=30)
            print(f"WORKER: Request finished with status code: {response.status_code}")
            response.raise_for_status()

            data = response.json()
            bot_reply = data.get("reply", "Sorry, I received an unexpected response.")
            print(f"WORKER: Got reply: '{bot_reply[:50]}...'")
            if self._is_running:
                print("WORKER: Emitting result signal.")
                self.signals.result.emit(bot_reply, "chatbot")
            else:
                print("WORKER: Worker stopped before emitting result.")

        except requests.exceptions.Timeout:
            error_msg = "Error: The request timed out."
            print(f"WORKER: Timeout error. {error_msg}")
            if self._is_running: self.signals.error.emit(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "Error: Could not connect to the chatbot server. Is it running?"
            print(f"WORKER: Connection error. {error_msg}")
            if self._is_running: self.signals.error.emit(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Error during request: {e}"
            print(f"WORKER: RequestException: {e}")
            try:
                 if e.response is not None:
                      error_msg = f"Error: Server returned status {e.response.status_code}."
                      print(f"WORKER: HTTP Status {e.response.status_code}")
                      server_error = e.response.json().get("error", e.response.text)
                      error_msg += f"\nServer message: {server_error}"
            except Exception as json_e:
                 print(f"WORKER: Could not parse error response: {json_e}")
                 pass
            if self._is_running: self.signals.error.emit(error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred in worker: {e}"
            print(f"WORKER: Generic Exception: {e}")
            import traceback
            traceback.print_exc()
            if self._is_running: self.signals.error.emit(error_msg)
        finally:
            print("WORKER: Reached finally block.")
            if self._is_running:
                print("WORKER: Emitting finished signal.")
                self.signals.finished.emit()
            else:
                print("WORKER: Worker stopped, not emitting finished.")

    def stop(self):
        print("WORKER: Stop requested.")
        self._is_running = False

class ChatbotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Chatbot")
        self.setGeometry(100, 100, 600, 650)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.input_layout = QHBoxLayout()
        self.button_layout = QHBoxLayout()

        self.chat_window = QTextEdit()
        self.chat_window.setReadOnly(True)
        self.chat_window.setStyleSheet("font-size: 11pt;")

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type your message here...")
        self.user_input.setStyleSheet("font-size: 12pt;")
        self.user_input.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("font-size: 10pt; padding: 5px;")
        self.send_button.clicked.connect(self.send_message)

        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.setStyleSheet("font-size: 10pt; padding: 5px;")
        self.clear_button.clicked.connect(self.clear_chat)

        self.main_layout.addWidget(self.chat_window)

        self.input_layout.addWidget(self.user_input)
        self.input_layout.addWidget(self.send_button)
        self.main_layout.addLayout(self.input_layout)

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.clear_button)
        self.main_layout.addLayout(self.button_layout)

        self.thread = None
        self.worker = None

        self.add_message_to_chat("Chatbot", "Hello! How can I help you today?", BOT_COLOR)

    def add_message_to_chat(self, sender, message, color):
        sender_html = f"<b style='color:{color};'>{sender}:</b>"
        message_html = message.replace("\n", "<br>")
        self.chat_window.append(f"{sender_html} {message_html}")

    def send_message(self):
        user_message = self.user_input.text().strip()
        if not user_message:
            return

        self.add_message_to_chat("User", user_message, USER_COLOR)
        self.user_input.clear()

        self.set_input_enabled(False)
        self.add_message_to_chat("Chatbot", "<i>Thinking...</i>", INFO_COLOR)

        self.thread = QThread()
        self.worker = ChatbotWorker(user_message)
        self.worker.moveToThread(self.thread)

        self.worker.signals.result.connect(self.handle_bot_reply)
        self.worker.signals.error.connect(self.handle_error)
        self.worker.signals.finished.connect(self.thread.quit)
        self.worker.signals.finished.connect(self.worker.deleteLater)
        self.worker.signals.finished.connect(self.thread.deleteLater)
        self.worker.signals.finished.connect(lambda: print("GUI: Worker finished signal received.")) # DEBUG
        self.worker.signals.finished.connect(lambda: self.set_input_enabled(True))

        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def handle_bot_reply(self, reply, tag):
        print(f"GUI: handle_bot_reply called with tag '{tag}' and reply: {reply[:60]}...") # DEBUG
        # self.remove_last_info_message() # --- TEMPORARILY DISABLED ---
        self.add_message_to_chat("Chatbot", reply, BOT_COLOR if tag == "chatbot" else ERROR_COLOR)

    def handle_error(self, error_message):
        print(f"GUI: handle_error called with message: {error_message}") # DEBUG
        # self.remove_last_info_message() # --- TEMPORARILY DISABLED ---
        self.add_message_to_chat("System", f"<i>{error_message}</i>", ERROR_COLOR)

    def remove_last_info_message(self):
         # This function remains here but is not called currently
         cursor = self.chat_window.textCursor()
         cursor.movePosition(cursor.End)
         cursor.select(cursor.BlockUnderCursor)
         last_block_html = cursor.selection().toHtml()

         if "Thinking..." in last_block_html and f"color:{INFO_COLOR}" in last_block_html:
             cursor.removeSelectedText()
             cursor.movePosition(cursor.End)
             cursor.select(cursor.BlockUnderCursor)
             if not cursor.selection().toPlainText().strip():
                 cursor.removeSelectedText()

         cursor.movePosition(cursor.End)
         self.chat_window.setTextCursor(cursor)


    def set_input_enabled(self, enabled):
        print(f"GUI: Setting input enabled: {enabled}") # DEBUG
        self.user_input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        if enabled:
            self.user_input.setFocus()

    def clear_chat(self):
        self.chat_window.clear()
        self.add_message_to_chat("Chatbot", "Chat cleared. How can I help you now?", BOT_COLOR)

    def closeEvent(self, event):
        print("GUI: Close event triggered.") # DEBUG
        if self.thread and self.thread.isRunning():
            print("GUI: Worker thread is running, attempting to stop.") # DEBUG
            if self.worker:
                 self.worker.stop()
            self.thread.quit()
            self.thread.wait(1000)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatbotGUI()
    window.show()
    sys.exit(app.exec())