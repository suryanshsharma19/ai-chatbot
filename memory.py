
class ConversationMemory:
    """
    A class to manage conversation history for maintaining context in a chatbot.
    """
    def __init__(self, max_history=10):
        # Initialize the conversation with a system prompt (optional, adapt as needed)
        self.system_prompt = "You are a helpful and friendly chatbot."
        self.conversation = []
        self.max_history = max_history

    def add_message(self, role, content):
        """
        Add a message to the conversation.

        Args:
            role (str): The role of the message sender ('user' or 'assistant').
            content (str): The message content.
        """
        self.conversation.append({"role": role, "content": content})
        # Keep memory size manageable
        if len(self.conversation) > self.max_history * 2 : 
             self.conversation.pop(0)
             self.conversation.pop(0)


    def get_conversation_history(self):
        """
        Retrieve the recent conversation history.

        Returns:
            list: A list of message dictionaries [{role: ..., content: ...}].
        """
        # Return a copy to prevent external modification
        return list(self.conversation)

    def get_formatted_history_string(self, include_system_prompt=True):
        """
        Formats the conversation history into a single string,
        suitable for models expecting plain text history.

        Returns:
            str: Formatted conversation string.
        """
        formatted = ""
        if include_system_prompt and self.system_prompt:
             formatted += f"System: {self.system_prompt}\n"
        for msg in self.conversation:
            role = "User" if msg["role"] == "user" else "Chatbot"
            formatted += f"{role}: {msg['content']}\n"
        return formatted.strip() # Remove trailing newline


    def clear_memory(self):
        """
        Clear the conversation memory.
        """
        self.conversation = []
