from langgraph.graph import StateGraph
from states.AnonymousState import AnonymousState
from nodes import memory_node,understand_query_node,error_handler_node,general_query_node,index_code_base_node,scaffold_project_node


def create_graph():
    builder=StateGraph(AnonymousState)

        
    builder.add_node("memroy_node",memory_node)
    builder.add_node("understand_query_node",understand_query_node)
    builder.add_node("error_handler_node",error_handler_node)
    builder.add_node("general_query_node",general_query_node)
    builder.add_node("index_code_base",index_code_base_node)
    builder.add_node("scaffold_project",scaffold_project_node)

    code_graph=builder.compile()