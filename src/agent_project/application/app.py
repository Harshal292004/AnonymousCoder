import os
import platform
from typing import Optional
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langfuse.langchain.CallbackHandler import LangchainCallbackHandler
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import StateSnapshot
from pydantic import BaseModel, Field

from src.agent_project.core.graph.graph import create_graph
from src.agent_project.core.prompts.system_prompt import get_system_prompt
from src.agent_project.core.states.AnonymousState import AnonymousState

from ..config.config import AppSettings
from ..infrastructure.databases.sql_database import (DataBaseManager,
                                                     get_database_manager)
from ..infrastructure.databases.vector_database import initialize_vector_store
from ..infrastructure.llm_clients.llms import GroqLLM, LLMConfig, ModelProvider
from ..infrastructure.monitoring.tracing import get_langfuse_handler
from ..utilities.logger import init_logger

# this is the application where everything starts
# lets work it out till only memory_node with the cli
# add a wrapper aorund everynode with

class Application(BaseModel):
    settings: AppSettings
    database: Optional[DataBaseManager] = Field(default=None)
    tracer: Optional[LangchainCallbackHandler] = Field(default=None)
    thread_id: str = Field(default="")
    graph: Optional[CompiledStateGraph] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self) -> None:
        log=init_logger(enable_logging=self.settings.LOGGING, log_file=self.settings.LOG_FILE)
        log.info("Warming up...")
        
        #intilialize chats db
        self.database = get_database_manager(self.settings.HISTORY_DB_FILE)
        
        #intilialize vector store with error handling
        try:
            embedding_model = HuggingFaceEmbeddings(
                model_name=self.settings.EMBEDDINGS_MODEL_NAME, 
                model_kwargs={"device": self.settings.DEVICE}
            )
            initialize_vector_store(db_file=self.settings.VECTOR_DB_FILE, embedding_model=embedding_model)
            log.info("Vector store initialized successfully")
        except Exception as e:
            log.warning(f"Could not initialize vector store: {e}")
            log.info("Continuing without vector store functionality")
        
        # create LLM
        try:
            llm_config = LLMConfig(provider=ModelProvider.GROQ, model_name=self.settings.LLM_NAME, api_key=self.settings.GROQ_API_KEY)
            llm = GroqLLM().create_llm(config=llm_config)
            log.info("LLM initialized successfully")
        except Exception as e:
            log.error(f"Could not initialize LLM: {e}")
            log.info("Continuing without LLM functionality")
            llm = None
        
        self.tracer = get_langfuse_handler(LANGFUSE_SECRET_KEY=self.settings.LANGFUSE_SECRET_KEY, LANGFUSE_HOST=self.settings.LANGFUSE_HOST, LANGFUSE_PUBLIC_KEY=self.settings.LANGFUSE_PUBLIC_KEY)
        
        self.thread_id = str(uuid4())
        
        # create Graph
        if llm:
            self.graph = create_graph(llm=llm)
            log.info("Graph created successfully")
        else:
            log.warning("Could not create graph due to LLM initialization failure")
            self.graph = None
            
        log.info("Running the AI hamsters...")

    def invoke(self):
        # invoke for chat
        self._chat()

    def _chat(self):
        #  intiate the data base with the current data base
        thread_id=str(uuid4())
        first_chat=True
        if self.settings.TRACING and self.tracer:
            config:RunnableConfig={"callbacks":[self.tracer],"configurable":{"thread_id":thread_id}}
        else:
            config:RunnableConfig={"configurable":{"thread_id":thread_id}}
            
        while True:
            # user input
            query=input("Enter your query please : ")
            # new message id
            message_id=str(uuid4())
            # add message to the data base
            self.database.add_human_message(thread_id=thread_id,message_id=message_id,content=query)
            current_state:StateSnapshot=self.graph.get_state(config=config)
            current_messages=current_state.values['messages']
        
            if query.lower() in {"bye","exit"}:
                print("Exiting the world...:(")
                break
            else:
                #run the graph with prompt history
                # append messages in the prompt with System Prompt
                if self.graph:
                    if first_chat:
                        first_chat=False
                        output=self.graph.invoke(AnonymousState(messages=[SystemMessage(get_system_prompt(os=platform.system(),path=os.getcwd())),HumanMessage(query)]),config)
                        print(output.get("content"))
                    else :
                        output=self.graph.invoke(AnonymousState(messages=current_messages+[HumanMessage(query)]))
                        print(output.get("content"))
                else:
                    print("❌ LLM not available. Please check your configuration.")
                
                
        print("="*60)
        
        # after clearning everything safe the thread by getting the state
        if self.graph:
            print(self.graph.get_state(config)) 
        else:
            print("❌ Graph not available")
        
        
        
        
        #TODO: after the execution get summary of recente chats in the thread and insert them as a context into the data base so we can refrecnce the chats
        #TODO: future feature