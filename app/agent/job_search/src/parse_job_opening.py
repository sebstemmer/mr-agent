from bs4 import BeautifulSoup
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from utils.common.src.config import settings
from utils.common.src.llm import CHAT_GPT_5_4_MINI_MODEL

_SYSTEM_PROMPT = (
    "Extract job opening details from the provided HTML. "
    "For the title, combine the job title and company name (e.g. 'Senior AI Engineer at Acme Corp'). "
    "For the summary, include: what the product/project is about "
    "and the key tasks and responsibilities. "
    "For requirements, extract the qualifications, experience, and skills required for the role. "
    "For link_to_company, extract the company website URL if present."
)


class ParsedJobOpening(BaseModel):
    title: str
    summary: str
    requirements: str
    link_to_company: str | None


class ParseJobOpening:
    def __init__(self):
        self._llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=CHAT_GPT_5_4_MINI_MODEL,
        ).with_structured_output(ParsedJobOpening)

    async def parse(self, html: str) -> ParsedJobOpening:
        text = BeautifulSoup(html, "html.parser").get_text(separator="\n", strip=True)
        return await self._llm.ainvoke(
            [SystemMessage(content=_SYSTEM_PROMPT), HumanMessage(content=text)],
        )
