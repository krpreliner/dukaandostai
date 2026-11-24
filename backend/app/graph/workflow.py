from langgraph.graph import StateGraph, START, END
from app.graph.state import DukaandostState
from app.graph.nodes import (
    goal_understanding_node,
    business_analysis_node,
    strategy_planning_node,
    task_prioritisation_node,
    supervisor_decision_node,
    financial_validation_node,
    human_approval_node,
    agent_execution_node,
    result_validation_node,
    business_metric_update_node,
    feedback_evaluation_node,
    handle_failure_node,
    replanning_or_completion_node
)
from app.memory.checkpoint import get_checkpointer

def route_after_supervisor(state: DukaandostState) -> str:
    if state.get("active_task") is None:
        return "replanning_or_completion"
    return "financial_validation"

def route_after_financial_validation(state: DukaandostState) -> str:
    active_task = state.get("active_task")
    if not active_task or active_task.get("status") == "FAILED":
        return "handle_failure"
    if active_task.get("approval_required", False):
        return "human_approval"
    return "agent_execution"

def route_after_human_approval(state: DukaandostState) -> str:
    active_task = state.get("active_task")
    if not active_task or active_task.get("status") == "REJECTED":
        return "handle_failure"
    return "agent_execution"


def build_dukaandost_graph():
    builder = StateGraph(DukaandostState)

    # Add Nodes
    builder.add_node("goal_understanding", goal_understanding_node)
    builder.add_node("business_analysis", business_analysis_node)
    builder.add_node("strategy_planning", strategy_planning_node)
    builder.add_node("task_prioritisation", task_prioritisation_node)
    builder.add_node("supervisor_decision", supervisor_decision_node)
    builder.add_node("financial_validation", financial_validation_node)
    builder.add_node("human_approval", human_approval_node)
    builder.add_node("agent_execution", agent_execution_node)
    builder.add_node("result_validation", result_validation_node)
    builder.add_node("business_metric_update", business_metric_update_node)
    builder.add_node("feedback_evaluation", feedback_evaluation_node)
    builder.add_node("handle_failure", handle_failure_node)
    builder.add_node("replanning_or_completion", replanning_or_completion_node)

    # Initial flow
    builder.add_edge(START, "goal_understanding")
    builder.add_edge("goal_understanding", "business_analysis")
    builder.add_edge("business_analysis", "strategy_planning")
    builder.add_edge("strategy_planning", "task_prioritisation")
    builder.add_edge("task_prioritisation", "supervisor_decision")

    # Routing from supervisor decision
    builder.add_conditional_edges(
        "supervisor_decision",
        route_after_supervisor,
        {
            "financial_validation": "financial_validation",
            "replanning_or_completion": "replanning_or_completion"
        }
    )

    # Routing from financial validation
    builder.add_conditional_edges(
        "financial_validation",
        route_after_financial_validation,
        {
            "human_approval": "human_approval",
            "agent_execution": "agent_execution",
            "handle_failure": "handle_failure"
        }
    )

    # Routing from human approval
    builder.add_conditional_edges(
        "human_approval",
        route_after_human_approval,
        {
            "agent_execution": "agent_execution",
            "handle_failure": "handle_failure"
        }
    )

    # Standard execution loop
    builder.add_edge("agent_execution", "result_validation")
    builder.add_edge("result_validation", "business_metric_update")
    builder.add_edge("business_metric_update", "feedback_evaluation")
    builder.add_edge("feedback_evaluation", "supervisor_decision")

    # Failure recovery loop back to supervisor
    builder.add_edge("handle_failure", "supervisor_decision")

    # Final completion
    builder.add_edge("replanning_or_completion", END)

    # Compile with persistent SQLite checkpointer
    checkpointer = get_checkpointer()
    graph = builder.compile(checkpointer=checkpointer)
    return graph
