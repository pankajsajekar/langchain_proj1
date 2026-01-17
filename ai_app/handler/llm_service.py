# handler/llm_service.py

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import asyncio
from ai_app.custom.opts import CHATGPT_MODEL_NAME
import logging

logging.basicConfig(level=logging.INFO)

class SimpleLLMHandler:
    """Simple LLM Handler without complex chain - Latest LangChain syntax"""
    
    def __init__(self, api_key: str, model_name: str = CHATGPT_MODEL_NAME, temperature: float = 0.7):
        self.llm = ChatOpenAI(
            api_key=api_key,  # Latest syntax
            model=model_name,
            temperature=temperature,
            streaming=False,
            verbose=True
        )
        self.chat_history = []

    async def get_response(self, user_message: str) -> str:
        """Get response from LLM with chat history"""
        try:
            # Add system message if first interaction
            if not self.chat_history:
                self.chat_history.append(
                    SystemMessage(content="You are a helpful AI assistant. Provide clear and concise answers.")
                )
            
            # Add user message
            self.chat_history.append(HumanMessage(content=user_message))
            
            # Get response asynchronously using ainvoke (latest async method)
            response = await self.llm.ainvoke(self.chat_history)
            
            # Add AI response to history
            self.chat_history.append(AIMessage(content=response.content))
            
            return response.content, response.usage_metadata['total_tokens']
            
        except Exception as e:
            return "Sorry, I couldn't process your request."
        
    async def stream_response(self, response: str, chunk_size: int = 5):
        """
        Stream an already-generated response in chunks.
        This function does NOT call the LLM, just streams the string.
        
        Args:
            response: The complete response text to stream
            chunk_size: Number of characters per chunk (default 5)
        """
        try:
            # Stream the response in chunks of chunk_size characters
            for i in range(0, len(response), chunk_size):
                chunk = response[i:i + chunk_size]
                yield chunk
                await asyncio.sleep(0.03)  # Small delay for smoother streaming
            
        except Exception as e:
            yield "Sorry, I couldn't stream the response."


    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []

    def get_history(self) -> list:
        """Get chat history"""
        return self.chat_history