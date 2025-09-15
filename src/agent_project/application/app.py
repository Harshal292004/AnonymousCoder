import os
import platform
from typing import Optional
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langfuse.langchain.CallbackHandler import LangchainCallbackHandler
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import StateSnapshot
from pydantic import BaseModel, Field

from ..config.config import AppSettings
from ..core.graph.graph import create_graph
from ..core.prompts.system_prompt import get_system_prompt, get_title_prompt
from ..core.states.AppStates import AppState
from ..infrastructure.databases.sql_database import (DataBaseManager,
                                                     get_database_manager)
from ..infrastructure.llm_clients.llms import LLMConfig, ModelProvider, get_llm
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
        # try:
        #     embedding_model = HuggingFaceEmbeddings(model_name=self.settings.EMBEDDINGS_MODEL_NAME)
        #     initialize_vector_store(
        #         host=self.settings.QDRANT_HOST, 
        #         api_key=self.settings.QDRANT_API_KEY, 
        #         embeddings=embedding_model,
        #         collection_name=self.settings.QDRANT_COLLECTION
        #     )
        #     log.info("Qdrant vector store initialized successfully")
        # except Exception as e:
        #     log.warning(f"Could not initialize Qdrant vector store: {e}")
        #     log.info("Continuing without vector store functionality")
        
        try:
            llm_config = LLMConfig(provider=ModelProvider.GROQ, model_name=self.settings.LLM_NAME, api_key=self.settings.LLM_API_KEY)
            self.llm = get_llm(llm_config)
            log.info("LLM initialized successfully")
        except Exception as e:
            log.error(f"Could not initialize LLM: {e}")
            log.info("Continuing without LLM functionality")
            self.llm = None
        
        self.tracer = get_langfuse_handler(LANGFUSE_SECRET_KEY=self.settings.LANGFUSE_SECRET_KEY, LANGFUSE_HOST=self.settings.LANGFUSE_HOST, LANGFUSE_PUBLIC_KEY=self.settings.LANGFUSE_PUBLIC_KEY)
        # create Graph
        if self.llm:
            self.graph = create_graph(llm=self.llm)
            log.info("Graph created successfully")
        else:
            log.warning("Could not create graph due to LLM initialization failure")
            self.graph = None
            
        log.info("Running the AI hamsters...")

    def invoke(self):
        # invoke for  a thread
        self._chat()

    def _chat(self):
        #  intiate the data base with the current data base
        thread_id=str(uuid4())
        first_chat=True
        SYSTEM_PROMPT:str=get_system_prompt(os=platform.system(),path=os.getcwd())
        if self.settings.TRACING and self.tracer:
            config:RunnableConfig={"callbacks":[self.tracer],"configurable":{"thread_id":thread_id}}
        else:
            config:RunnableConfig={"configurable":{"thread_id":thread_id}}
        
        if self.database is None or self.llm is None:
            return
        
        # new thread
        self.database.create_thread(thread_id=thread_id,title="")    
        while True:
            # user input
            query=input("Enter your query please : ")
            # add message to the data base
            self.database.add_human_message(thread_id=thread_id,message_id=str(uuid4()),content=query)
            current_state:StateSnapshot=self.graph.get_state(config=config)
            # accquire previous messages
            current_messages=current_state.values['messages']
            type=current_state.values['type']
            
            if query.lower() in {"bye","exit"}:
                print("Exiting the world...:(")
                break
            else:
                # run the graph with prompt history
                # append messages in the prompt with System Prompt
                if self.graph:
                    if first_chat:
                        first_chat=False
                        output=self.graph.invoke(AppState(type="execution_node",query=query,messages=[SystemMessage(content=SYSTEM_PROMPT)]),config)
                        output=output.get("content")
                        print(output)     
                        self.database.add_ai_message(thread_id=thread_id,message_id=str(uuid4()),content=str(output))
                        output_title=self.llm.invoke(input=[SystemMessage(content=get_title_prompt()),HumanMessage(content=query),AIMessage(content=str(output))])
                        self.database.alter_thread_title(thread_id,str(output_title.content))
                    else :
                        output=self.graph.invoke(AppState(type=type,query=query,messages=current_messages))
                        print(output.get("content"))
                        self.database.add_ai_message(thread_id=thread_id,message_id=str(uuid4()),content=str(output.get("content")))
                else:
                    print("LLM not available. Please check your configuration.")
                
                
        print("="*60)
        
        #TODO: after the execution get summary of recent chats in the thread and insert them as a context into the data base so we can refrecnce the chat