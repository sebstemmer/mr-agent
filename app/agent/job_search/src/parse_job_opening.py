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
    "For rating, rate the job 1 (not interesting), 2 (somewhat interesting), or 3 (very interesting) "
    "based on the following criteria: {rating_prompt} "
    "For rating_reason, briefly explain why you gave this rating. "
    "For link_to_company, extract the company website URL if present."
)


class ParsedJobOpening(BaseModel):
    title: str
    summary: str
    requirements: str
    link_to_company: str | None
    rating: int
    rating_reason: str


class ParseJobOpening:
    def __init__(self):
        self._llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=CHAT_GPT_5_4_MINI_MODEL,
        ).with_structured_output(ParsedJobOpening)
        self._system_prompt = _SYSTEM_PROMPT.format(
            rating_prompt=settings.JOB_OPENING_RATING_PROMPT,
        )

    async def parse(self, html: str) -> ParsedJobOpening:
        text = BeautifulSoup(html, "html.parser").get_text(separator="\n", strip=True)
        return await self._llm.ainvoke(
            [SystemMessage(content=self._system_prompt), HumanMessage(content=text)],
        )
