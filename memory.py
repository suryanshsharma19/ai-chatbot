
class ConversationMemory:
    # Manages conversation history to keep track of context
    def __init__(self, max_history=10):
        # Set up the system prompt and conversation history
        self.system_prompt = "You are a helpful and friendly chatbot."
        self.conversation = []
        self.max_history = max_history

    def add_message(self, role, content):
        # Add a new message from either user or assistant to the conversation
        self.conversation.append({"role": role, "content": content})
        # Don't let the conversation history get too long
        if len(self.conversation) > self.max_history * 2 : 
             self.conversation.pop(0)
             self.conversation.pop(0)


    def get_conversation_history(self):
        # Get the conversation history as a list
        # Return a copy to prevent external modification
        return list(self.conversation)

    def get_formatted_history_string(self, include_system_prompt=True):
        # Convert conversation to a formatted string for models that need text input
        formatted = ""
        if include_system_prompt and self.system_prompt:
             formatted += f"System: {self.system_prompt}\n"
        for msg in self.conversation:
            role = "User" if msg["role"] == "user" else "Chatbot"
            formatted += f"{role}: {msg['content']}\n"
        return formatted.strip() # Remove trailing newline


    def clear_memory(self):
        # Reset the conversation history
        self.conversation = []
