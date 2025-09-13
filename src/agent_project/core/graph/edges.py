from ..states.AppStates import AppState


def route_edge(state:AppState):
    return "execution_node" if state.type == "execution_node" else "scaffolding_node"