from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
from src.agent_project.infrastructure.llm_clients.llms import LLMConfig,ModelProvider,GoogleLLM
config= LLMConfig(
    provider=ModelProvider.GOOGLE,
    model_name= 'gemini-2.5-flash-lite',
    api_key='AIzaSyBrhpNzPdMmOOLJ-_ameGsQgBp4_TXBOxQ',
)
llm=GoogleLLM().create_llm(config=config)

print(llm.invoke([SystemMessage("You are conversing with Harshal"),HumanMessage("Who am I?")]))

