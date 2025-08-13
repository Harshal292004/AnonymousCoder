from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator,model_validator
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import os
from tenacity import retry, stop_after_attempt, wait_exponential


class ModelProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    GOOGLE = "google"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"  # For future use


class ModelType(str, Enum):
    """Common model types across providers."""
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GEMINI_PRO = "gemini-pro"
    GEMINI_FLASH = "gemini-flash"
    LLAMA2 = "llama2"
    MISTRAL = "mistral"
    CUSTOM = "custom"


class ModelParameters(BaseModel):
    """Unified model parameters with validation."""
    max_retries: int = Field(default=3, ge=1, le=10, description="Number of retries for the model if error occurs")
    max_tokens: int = Field(default=4096, ge=1, le=1000000, description="Number of output tokens")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0, description="The temperature of the model")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="Top-p sampling parameter")
    top_k: Optional[int] = Field(default=None, ge=1, le=100, description="Top-k sampling parameter")
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0, description="Frequency penalty")
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0, description="Presence penalty")
    stop: Optional[List[str]] = Field(default=None, description="Stop sequences")
    timeout: Optional[int] = Field(default=60, ge=1, le=300, description="Request timeout in seconds")
    
    @validator('top_p')
    def validate_top_p(cls, v):
        if v == 0.0:
            raise ValueError("top_p cannot be 0.0, use 1.0 for no top-p sampling")
        return v


class LLMConfig(BaseModel):
    """Configuration for LLM instances."""
    provider: ModelProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    parameters: ModelParameters = Field(default_factory=ModelParameters)
    custom_headers: Optional[Dict[str, str]] = None
    
    class Config:
        extra = "forbid"


class BaseLLMFactory(ABC):
    """Abstract factory for creating LLM instances."""
    
    @abstractmethod
    def create_llm(self, config: LLMConfig) -> BaseChatModel:
        """Create an LLM instance based on configuration."""
        pass


class OpenAILLMFactory(BaseLLMFactory):
    """Factory for OpenAI LLM instances."""
    
    def create_llm(self, config: LLMConfig) -> BaseChatModel:
        if not config.api_key and not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key is required")
        
        api_key = config.api_key or os.getenv("OPENAI_API_KEY")
        
        return ChatOpenAI(
            model=config.model_name,
            openai_api_key=api_key,
            openai_api_base=config.base_url,
            max_tokens=config.parameters.max_tokens,
            temperature=config.parameters.temperature,
            top_p=config.parameters.top_p,
            frequency_penalty=config.parameters.frequency_penalty,
            presence_penalty=config.parameters.presence_penalty,
            stop=config.parameters.stop,
            timeout=config.parameters.timeout,
            max_retries=config.parameters.max_retries,
            headers=config.custom_headers
        )


class GoogleLLMFactory(BaseLLMFactory):
    """Factory for Google LLM instances."""
    
    def create_llm(self, config: LLMConfig) -> BaseChatModel:
        if not config.api_key and not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("Google API key is required")
        
        api_key = config.api_key or os.getenv("GOOGLE_API_KEY")
        
        return ChatGoogleGenerativeAI(
            model=config.model_name,
            google_api_key=api_key,
            max_output_tokens=config.parameters.max_tokens,
            temperature=config.parameters.temperature,
            top_p=config.parameters.top_p,
            top_k=config.parameters.top_k,
            stop_sequences=config.parameters.stop,
            timeout=config.parameters.timeout,
            max_retries=config.parameters.max_retries
        )


class OllamaLLMFactory(BaseLLMFactory):
    """Factory for Ollama LLM instances."""
    
    def create_llm(self, config: LLMConfig) -> BaseChatModel:
        base_url = config.base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        return ChatOllama(
            model=config.model_name,
            base_url=base_url,
            temperature=config.parameters.temperature,
            top_p=config.parameters.top_p,
            top_k=config.parameters.top_k,
            stop=config.parameters.stop,
            timeout=config.parameters.timeout,
            num_predict=config.parameters.max_tokens
        )


class LLMManager:
    """Unified manager for different LLM providers."""
    
    def __init__(self):
        self._factories: Dict[ModelProvider, BaseLLMFactory] = {
            ModelProvider.OPENAI: OpenAILLMFactory(),
            ModelProvider.GOOGLE: GoogleLLMFactory(),
            ModelProvider.OLLAMA: OllamaLLMFactory(),
        }
        self._instances: Dict[str, BaseChatModel] = {}
        self.logger = logging.getLogger(__name__)
    
    def get_llm(self, config: LLMConfig) -> BaseChatModel:
        """Get or create an LLM instance based on configuration."""
        cache_key = f"{config.provider}:{config.model_name}:{config.parameters.json()}"
        
        if cache_key not in self._instances:
            try:
                factory = self._factories.get(config.provider)
                if not factory:
                    raise ValueError(f"Unsupported provider: {config.provider}")
                
                self._instances[cache_key] = factory.create_llm(config)
                self.logger.info(f"Created new LLM instance: {config.provider}:{config.model_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to create LLM instance: {e}")
                raise
        
        return self._instances[cache_key]
    
    def get_llm_by_name(self, provider: ModelProvider, model_name: str, **kwargs) -> BaseChatModel:
        """Convenience method to get LLM with default parameters."""
        config = LLMConfig(
            provider=provider,
            model_name=model_name,
            **kwargs
        )
        return self.get_llm(config)
    
    def clear_cache(self):
        """Clear cached LLM instances."""
        self._instances.clear()
        self.logger.info("Cleared LLM cache")
    
    def list_instances(self) -> List[str]:
        """List all cached LLM instances."""
        return list(self._instances.keys())


class LLMClient:
    """High-level client for LLM operations with retry logic and error handling."""
    
    def __init__(self, manager: LLMManager):
        self.manager = manager
        self.logger = logging.getLogger(__name__)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def generate_response(
        self,
        messages: List[BaseMessage],
        config: LLMConfig,
        stream: bool = False
    ) -> Union[str, Any]:
        """Generate response from LLM with retry logic."""
        try:
            llm = self.manager.get_llm(config)
            
            if stream:
                return llm.stream(messages)
            else:
                response = await llm.ainvoke(messages)
                return response.content
                
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise
    
    def create_simple_chain(
        self,
        config: LLMConfig,
        system_prompt: Optional[str] = None
    ):
        """Create a simple chain with the specified LLM."""
        llm = self.manager.get_llm(config)
        
        if system_prompt:
            chain = (
                {"system": RunnablePassthrough(), "user": RunnablePassthrough()}
                | llm
                | StrOutputParser()
            )
        else:
            chain = llm | StrOutputParser()
        
        return chain
    
    def batch_generate(
        self,
        prompts: List[str],
        config: LLMConfig,
        system_prompt: Optional[str] = None
    ) -> List[str]:
        """Generate responses for multiple prompts in batch."""
        llm = self.manager.get_llm(config)
        messages_list = []
        
        for prompt in prompts:
            if system_prompt:
                messages = [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]
            else:
                messages = [HumanMessage(content=prompt)]
            messages_list.append(messages)
        
        # Use batch processing if available
        try:
            responses = llm.batch(messages_list)
            return [response.content for response in responses]
        except AttributeError:
            # Fallback to sequential processing
            self.logger.warning("Batch processing not available, falling back to sequential")
            responses = []
            for messages in messages_list:
                response = llm.invoke(messages)
                responses.append(response.content)
            return responses


# Convenience functions for common use cases
def create_openai_llm(
    model_name: str = "gpt-3.5-turbo",
    api_key: Optional[str] = None,
    **kwargs
) -> BaseChatModel:
    """Create an OpenAI LLM instance."""
    config = LLMConfig(
        provider=ModelProvider.OPENAI,
        model_name=model_name,
        api_key=api_key,
        parameters=ModelParameters(**kwargs)
    )
    manager = LLMManager()
    return manager.get_llm(config)


def create_google_llm(
    model_name: str = "gemini-pro",
    api_key: Optional[str] = None,
    **kwargs
) -> BaseChatModel:
    """Create a Google LLM instance."""
    config = LLMConfig(
        provider=ModelProvider.GOOGLE,
        model_name=model_name,
        api_key=api_key,
        parameters=ModelParameters(**kwargs)
    )
    manager = LLMManager()
    return manager.get_llm(config)


def create_ollama_llm(
    model_name: str = "llama2",
    base_url: Optional[str] = None,
    **kwargs
) -> BaseChatModel:
    """Create an Ollama LLM instance."""
    config = LLMConfig(
        provider=ModelProvider.OLLAMA,
        model_name=model_name,
        base_url=base_url,
        parameters=ModelParameters(**kwargs)
    )
    manager = LLMManager()
    return manager.get_llm(config)


# Example usage and testing
if __name__ == "__main__":
    # Example: Create and use different LLM providers
    manager = LLMManager()
    
    # OpenAI example
    openai_config = LLMConfig(
        provider=ModelProvider.OPENAI,
        model_name="gpt-3.5-turbo",
        parameters=ModelParameters(temperature=0.7, max_tokens=1000)
    )
    
    # Google example
    google_config = LLMConfig(
        provider=ModelProvider.GOOGLE,
        model_name="gemini-pro",
        parameters=ModelParameters(temperature=0.5, max_tokens=2000)
    )
    
    # Ollama example
    ollama_config = LLMConfig(
        provider=ModelProvider.OLLAMA,
        model_name="llama2",
        parameters=ModelParameters(temperature=0.3, max_tokens=1500)
    )
    
    print("LLMManager initialized successfully!")
    print(f"Supported providers: {[p.value for p in ModelProvider]}")