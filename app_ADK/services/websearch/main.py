"""
Web Search Agent — A2A compliant microservice.
Runs on port 8003.

Mock implementation with smart query parsing.
Swap handle() body for Brave Search / SerpAPI in production.
"""

import logging
from app_ADK.core.a2a_base_service import A2ABaseService
from app_ADK.core.a2a_models import AgentCard, AgentSkill
from app_ADK.core.config import AGENT_URLS
from app_ADK.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# ── Mock knowledge base ────────────────────────────────────────────────────────
# In production: replace handle() with a real Brave/SerpAPI call

ZIP_CODES = {
    "delhi":    "110001",
    "mumbai":   "400001",
    "london":   "EC1A 1BB",
    "new york": "10001",
    "tokyo":    "100-0001",
    "paris":    "75001",
    "sydney":   "2000",
}


def _extract_zip(query: str) -> dict | None:
    """
    If the query is asking for a zip/postal code for a known city,
    return it directly from the mock knowledge base.
    """
    q = query.lower()
    if not any(kw in q for kw in ["zip", "postal", "pin code", "postcode"]):
        return None

    for city, zip_code in ZIP_CODES.items():
        if city in q:
            return {
                "query":    query,
                "city":     city.title(),
                "zip_code": zip_code,
                "source":   "mock_knowledge_base",
            }
    return None


class SearchService(A2ABaseService):
    card = AgentCard(
        name="search_agent",
        description=(
            "Searches the web for any query. "
            "Can look up zip codes, postal codes, news, facts, and general information."
        ),
        url=AGENT_URLS["search_agent"],
        skills=[
            AgentSkill(name="search_web",    description="Search the web for any query"),
            AgentSkill(name="zip_code_lookup", description="Find zip/postal code for a city"),
        ],
        planner_hint=(
            "Use for: web search, news, general knowledge, current events, "
            "zip codes, postal codes, pin codes. "
            "For zip/postal codes use query format: 'zip code of <city>'. "
            "Call once per city when looking up zip codes for multiple cities."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query. E.g. 'zip code of Delhi' or 'latest AI news'",
                }
            },
            "required": ["query"],
        },
        tags=["search", "web", "news", "internet", "zip", "postal", "pincode"],
    )

    async def handle(self, query: str) -> dict:
        logger.info("SearchService.handle | query: %s", query)

        # fast path: zip code lookup
        zip_result = _extract_zip(query)
        if zip_result:
            logger.info("ZIP lookup hit | city=%s | zip=%s",
                        zip_result["city"], zip_result["zip_code"])
            return zip_result

        # general search — mock results
        # swap this block with real API in production:
        # async with httpx.AsyncClient() as c:
        #     r = await c.get("https://api.search.brave.com/res/v1/web/search",
        #                     headers={"X-Subscription-Token": BRAVE_API_KEY},
        #                     params={"q": query})
        #     return r.json()

        results = [
            {
                "title":   f"Everything about '{query}'",
                "snippet": f"Comprehensive overview of {query}.",
                "url":     f"https://example.com/search?q={query.replace(' ', '+')}",
            },
            {
                "title":   f"{query} — Wikipedia",
                "snippet": f"Wikipedia article on {query}.",
                "url":     f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
            },
            {
                "title":   f"Latest news: {query}",
                "snippet": f"Recent updates on {query}.",
                "url":     f"https://news.example.com/?q={query.replace(' ', '+')}",
            },
        ]
        return {"query": query, "count": len(results), "results": results}


app = SearchService().build_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app_ADK.services.websearch.main:app", host="0.0.0.0", port=8003, reload=True)
