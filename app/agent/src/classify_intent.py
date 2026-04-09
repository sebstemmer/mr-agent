from logging import Logger

from conversation.src.handle_conversation import HandleConversation
from conversation.src.handle_conversation_tool import HandleConversationTool
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from weather.src.handle_weather import HandleWeather
from weather.src.handle_weather_tool import HandleWeatherTool


class ClassifyIntent:
    def __init__(
        self,
        api_key: str,
        model: str,
        handle_conversation: HandleConversation,
        handle_conversation_tool: HandleConversationTool,
        handle_weather: HandleWeather,
        handle_weather_tool: HandleWeatherTool,
        logger: Logger,
    ):
        self._handle_conversation = handle_conversation
        self._handle_weather = handle_weather
        self._logger = logger

        # noinspection PyTypeChecker
        llm = ChatOpenAI(api_key=api_key, model=model)
        self._llm = llm.bind_tools(
            [handle_conversation_tool, handle_weather_tool],
            tool_choice="required",
        )

    async def classify(self, messages: list[BaseMessage]) -> dict:
        response = await self._llm.ainvoke(messages)

        # noinspection PyTypeChecker
        tool_call = response.tool_calls[0]

        tool_name = tool_call["name"]
        self._logger.info("[classify] tool=%s", tool_name)

        if tool_name == "handle_weather":
            return await self._handle_weather.handle(messages=messages)

        message = await self._handle_conversation.handle(messages=messages)
        return {"messages": [message], "current_branch": None}
