# Lab 10 Written Answers

## Graded Task 1 Reflection Question

Changing only the prompts and node behavior shows that LangGraph separates
domain expertise from workflow architecture. The state schema still stores the
same kind of shared memory, and the graph still follows the same
generator-critic-revise loop. Only the meaning of the generator and critic work
changed from essay writing to FYP feedback. In a production system, a domain
expert would usually edit `reflection/nodes.py`, especially the prompts and
review criteria. A software architect would own `reflection/graph.py` because it
controls flow, routing, and graph structure. This separation makes the agent
easier to maintain because domain changes do not require rewiring the graph.

## Tool Use Alignment Table

| Lab 08 manual component | LangGraph equivalent | File |
| --- | --- | --- |
| `TOOL_SCHEMAS = [{...}]` | Tool schemas generated from typed `@tool` functions in `TOOLS` | `grade_advisor/tools.py` |
| `TOOL_FUNCTIONS = {'name': func}` | `TOOL_BY_NAME` maps tool names to executable tool objects | `grade_advisor/tools.py` |
| `for turn in range(max_turns)` | `StateGraph` loop with `turn_count` and `max_turns` in state | `grade_advisor/graph.py` |
| `if not message.tool_calls: return` | `should_use_tools()` returns `done` when last AI message has no tool calls | `grade_advisor/graph.py` |
| `messages.append(tool_result)` | `messages: Annotated[list, add_messages]` appends `ToolMessage` results | `grade_advisor/state.py` |
| `execute_tool(name, arguments)` | `tool_node()` reads `tool_calls`, invokes `TOOL_BY_NAME[name]`, and logs results | `grade_advisor/nodes.py` |

## Take-Home Explanation

In Lab 08, the Tool Use Pattern was controlled manually with a loop, message
list, tool schema list, and explicit dispatch code. In this LangGraph version,
the same responsibilities are still present, but they are separated into state,
nodes, edges, and a routing function. The LLM still decides which tool to call,
and the Python code still executes trusted local tools. What changed is that
the loop is now represented as a graph: `llm` routes to `tools` when tool calls
exist, and `tools` routes back to `llm` after returning observations. The state
keeps the conversation history, tool log, turn count, and final answer in one
typed structure. This makes the flow easier to visualize, test, and extend. A
new academic tool can be added without rewriting the whole loop. The main idea
stayed the same: the model reasons, tools provide real data, and the final
answer is grounded in tool results.
