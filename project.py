'''
litrev_backend.py
=================
Core logic for the multi‑agent literature‑review assistant built with the
**AutoGen** AgentChat stack (⩾ v0.4).  It exposes a single public coroutine
`run_litrev()` that drives a two‑agent team:

* **search_agent** – crafts an arXiv query and fetches papers via the provided
  `arxiv_search` tool.
* **summarizer** – writes a short Markdown literature review from the selected
  papers.

The module is deliberately self‑contained so it can be reused in CLI apps,
Streamlit, FastAPI, Gradio, etc.
'''
from __future__ import annotations
import os
import asyncio
from typing import AsyncGenerator, Dict, List

import arxiv 
from autogen_core.tools import FunctionTool
from autogen_agentchat.agents import AssistantAgent,UserProxyAgent
from autogen_agentchat.messages import (
    TextMessage
)
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

def build_team(model: str = "gpt-4o-mini") -> RoundRobinGroupChat:
    """Create and return a three‑agent *RoundRobinGroupChat* team."""
    key = os.getenv('OPENAI_API_KEY')
    llm_client = OpenAIChatCompletionClient(model=model,api_key=key)
    # Agent that **only** calls the arXiv tool and forwards top‑N papers

    user_agent = UserProxyAgent(
    name="UserProxy",
    description='You are an aspiring entrepreneur.\n'
    'You provide a startup idea in 2–5 sentences.\n'
    'Clearly describe the product/service, target audience, and unique value proposition.',
    input_func=input
    )


    market_agent = AssistantAgent(
        name="market_agent",
        description="make a comprehensive market research.",
        system_message=(
            "You are a Market Research Analyst.\n"
            "Your role is to evaluate the startup idea by analyzing the target market,\n"
            "existing competitors, potential demand, and entry barriers."
        ),
        model_client=llm_client,
        reflect_on_tool_use=True,
    )

    # Agent that writes the final literature review
    financial_agent = AssistantAgent(
        name="financial_agent",
        description="Produces a short Markdown review from provided papers.",
        system_message=(
            "You are a Financial Analyst.\n"
            "Your role is to provide a rough financial evaluation of the startup idea.\n"
            "Estimate initial costs, revenue potential, break-even point, and profitability.\n"
            "Make assumptions explicit and keep numbers realistic but approximate.\n"
        ),
        model_client=llm_client,
    )

    tech_agent = AssistantAgent(
        name="tech_agent",
        description="Produces a short Markdown review from provided papers.",
        system_message=(
            "You are a Technology Expert.\n"
            "Your role is to evaluate the technical feasibility of the startup idea.\n"
            "Discuss the tech stack, scalability, potential technical risks,\n"
            "and required infrastructure. Suggest alternatives if the idea is not feasible.\n"
        ),
        model_client=llm_client,
    )

    return RoundRobinGroupChat(
        participants=[market_agent, financial_agent, tech_agent, user_agent],
        max_turns=2,
    )


async def run_startup_eval(
    topic: str,
    model: str = "gpt-4o-mini",
) -> AsyncGenerator[str, None]:
    """Yield strings representing the conversation in real‑time."""

    team = build_team(model=model)
    task_prompt = (
        f"Evaluate this startup idea:  **{topic}** "
    )

    async for msg in team.run_stream(task=task_prompt):
        if isinstance(msg, TextMessage):
            yield f"{msg.source}: {msg.content}"


if __name__ == "__main__":
    async def _demo() -> None:
        async for line in run_startup_eval("Artificial Intelligence"):
            print(line)

    asyncio.run(_demo()) 
