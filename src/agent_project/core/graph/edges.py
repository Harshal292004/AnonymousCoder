from ..states.AppStates import AnonymousState


def route_edge(state:AnonymousState):
    return "execution_node" if state.type == "execution_node" else "scaffolding_node"