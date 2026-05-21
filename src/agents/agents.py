from dataclasses import dataclass

from langgraph.graph.state import CompiledStateGraph
from langgraph.pregel import Pregel

from .xbuddy.agent import graph as xbuddy_agent
from schema import AgentInfo

DEFAULT_AGENT = "xbuddy"

AgentGraph = CompiledStateGraph | Pregel


@dataclass
class Agent:
    description: str
    graph: AgentGraph


agents: dict[str, Agent] = {
    "xbuddy": Agent(
        description="FitnessBuddy — guides users through 5 sections (goals, fitness, schedule, nutrition, lifestyle) to produce a personalised training program.",
        graph=xbuddy_agent,
    ),
}


def get_agent(agent_id: str) -> AgentGraph:
    return agents[agent_id].graph


def get_all_agent_info() -> list[AgentInfo]:
    return [
        AgentInfo(key=agent_id, description=agent.description)
        for agent_id, agent in agents.items()
    ]
