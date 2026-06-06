from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import re

from .models import IntentResult, Intent
from .prompt import INTENT_PROMPT


class IntentPlanner:
    def __init__(self, llm):
        self.chain = (
            ChatPromptTemplate.from_messages(
                [("system", INTENT_PROMPT), ("human", "{query}")]
            )
            | llm
            | StrOutputParser()
        )

    async def run(self, query: str) -> IntentResult:
        raw_text = await self.chain.ainvoke({"query": query})

        try:
            data = json.loads(raw_text.strip())
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except Exception:
                    data = {"intent": "general", "confidence": 1.0}
            else:
                data = {"intent": "general", "confidence": 1.0}

        intent_str = data.get("intent", "general")
        try:
            intent = Intent(intent_str)
        except json.JSONDecodeError:
            intent = Intent.GENERAL

        return IntentResult(intent=intent, confidence=data.get("confidence", 1.0))
