from langchain_core.messages import ToolMessage
from langchain_core.messages.tool import ToolCall
from langchain_core.tools import BaseTool

from agent.agent.src.state.agent_state import ExecutedToolAction
from agent.agent.src.state.dispatch_executed_tool_action import (
    DispatchExecutedToolAction,
)


async def invoke_tool(
    tool: BaseTool,
    call: ToolCall,
    dispatch_executed_tool_action: DispatchExecutedToolAction,
    error_message: str,
) -> ExecutedToolAction:
    try:
        result = await tool.ainvoke(input=call)
    except Exception:
        return await dispatch_executed_tool_action.dispatch(
            tool_message=ToolMessage(
                content=error_message,
                tool_call_id=call["id"],
                status="error",
            ),
            readable_tool_message=error_message,
        )

    return await dispatch_executed_tool_action.dispatch(
        tool_message=ToolMessage(
            content=result.content,
            tool_call_id=call["id"],
        ),
        readable_tool_message=result.artifact,
    )
