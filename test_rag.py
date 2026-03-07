import asyncio
import logging
from resonite_mcp.rag import rag_engine

logging.basicConfig(level=logging.INFO)


async def test_rag():
    print("Initializing RAG...")
    await rag_engine.initialize()

    query = "How to create a ProtoFlux script?"
    print(f"Searching for: {query}")
    results = await rag_engine.search(query, limit=2)

    print(f"Found {len(results)} results:")
    for i, r in enumerate(results):
        print(f"[{i + 1}] {r['title']} ({r['filename']}) - Score: {r['score']}")
        print(f"Text Snippet: {r['text'][:200]}...")
        print("-" * 40)


if __name__ == "__main__":
    asyncio.run(test_rag())
