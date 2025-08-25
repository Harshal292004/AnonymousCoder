import os
import platform
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from pydantic import BaseModel

from src.agent_project.core.graph.graph import create_graph
from src.agent_project.core.prompts.system_prompt import get_system_prompt
from src.agent_project.core.states.AnonymousState import AnonymousState

from ..config.config import AppSettings
from ..infrastructure.databases.sql_database import get_database_manager
from ..infrastructure.databases.vector_database import initialize_vector_store
from ..infrastructure.llm_clients.llms import GroqLLM, LLMConfig, ModelProvider
from ..infrastructure.monitoring.tracing import get_langfuse_handler
from ..utilities.logger import get_logger

# this is the application where everything starts
# lets work it out till only memory_node with the cli
# add a wrapper aorund everynode with

class Application(BaseModel):

    def __init__(self,settings:AppSettings):
        log=get_logger(enable_logging=settings.LOGGING,log_file=settings.LOG_FILE)
        log.info("Warming up...")
        self.settings=settings
        
        #intilialize chats db
        self.database=get_database_manager(settings.HISTORY_DB_FILE)
        
        #intilialize vector store
        initialize_vector_store(db_file=settings.VECTOR_DB_FILE,embedding_model=HuggingFaceEmbeddings(model_name=settings.EMBEDDINGS_MODEL_NAME, model_kwargs={"device":settings.DEVICE}))
        
        # create LLM
        llm_config=LLMConfig(provider=ModelProvider.GROQ,model_name=settings.LLM_NAME,api_key=settings.GROQ_API_KEY)
        llm=GroqLLM().create_llm(config=llm_config)
        
        
        self.tracer=get_langfuse_handler(LANGFUSE_SECRET_KEY=settings.LANGFUSE_SECRET_KEY,LANGFUSE_HOST=settings.LANGFUSE_HOST,LANGFUSE_PUBLIC_KEY=settings.LANGFUSE_PUBLIC_KEY)
        
        self.thread_id=str(uuid4())
        
        # create Graph
        self.graph=create_graph(llm=llm)
        log.info("Running the AI hamsters...")

    def invoke(self):
        # invoke for chat
        self._chat()

    def _chat(self):
        #  intiate the data base with the current data base
        thread_id=str(uuid4())
        if self.settings.TRACING:
            config:RunnableConfig={"callbacks":[self.tracer],"configurable":{"thread_id":thread_id}}
        else:
            config:RunnableConfig={"configurable":{"thread_id":thread_id}}
            
        while True:
            query=input("Enter your query please : ")
            message_id=str(uuid4())
            self.database.add_human_message(thread_id=thread_id,message_id=message_id,content=query)
            if query.lower() in {"bye","exit"}:
                print("Exiting the world...:(")
                break
            else:
                #run the graph with prompt history
                # append messages in the prompt with System Prompt
                output=self.graph.invoke(AnonymousState(messages=[SystemMessage(get_system_prompt(os=platform.system(),path=os.getcwd())),HumanMessage(query)]),config)
                print(output)
                
                
        print("="*60)
        
        # after clearning everything safe the thread by getting the state
        print(self.graph.get_state(config)) 
        
        
        
        
        #TODO: after the execution get summary of recente chats in the thread and insert them as a context into the data base so we can refrecne the chats
        #TODO: future feature