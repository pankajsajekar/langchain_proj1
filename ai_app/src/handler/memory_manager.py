# from langchain.memory import ConversationBufferWindowMemory
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage
from django.contrib.auth.models import User
from ai_app.models import AIChats  # Assuming AIChats is your model
from channels.db import database_sync_to_async
import logging

logging.basicConfig(level=logging.INFO)

class MemoryManager:
    """Manages conversation memory using ConversationBufferWindowMemory, loaded from DB."""
    
    def __init__(self, user: User, window_size: int = 10):
        """
        Initialize memory manager for a user.
        
        Args:
            user: Django User instance
            window_size: Number of recent messages to keep in memory (default 10)
        """
        self.user = user
        self.window_size = window_size
        self.memory = ConversationBufferMemory(k=window_size, return_messages=True)
        # Note: Async loading is handled in the handler's init to avoid sync issues
    
    @database_sync_to_async
    def load_history_from_db(self):
        """Load chat history from AIChats model and populate memory."""
        try:
            chats = AIChats.objects.filter(user=self.user).order_by('-created_at')[:5] 
            for chat in chats:
                # Add user message
                self.memory.chat_memory.add_message(HumanMessage(content=chat.message))
                # Add AI response
                self.memory.chat_memory.add_message(AIMessage(content=chat.response))
            logging.info(f"Loaded {len(chats)} chat pairs from DB for user {self.user.username}")
        except Exception as e:
            logging.error(f"Error loading chat history from DB: {e}")
    
    def add_message(self, user_message: str, ai_response: str):
        """Add a new user message and AI response to memory."""
        self.memory.chat_memory.add_message(HumanMessage(content=user_message))
        self.memory.chat_memory.add_message(AIMessage(content=ai_response))
    
    def get_memory(self):
        """Get the current memory object."""
        return self.memory
    
    def clear_memory(self):
        """Clear the memory."""
        self.memory.clear()
    
    @database_sync_to_async
    def save_to_db(self, user_message: str, ai_response: str, tokens_used: int = 0):
        """Save a new chat to DB."""
        try:
            AIChats.objects.create(
                user=self.user,
                message=user_message,
                response=ai_response,
                tokens_used=tokens_used
            )
            logging.info(f"Saved chat to DB for user {self.user.username}")
        except Exception as e:
            logging.error(f"Error saving chat to DB: {e}")