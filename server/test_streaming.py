import asyncio
from server.service.agents.product_agent import ProductAgent

async def test_streaming():
    agent = ProductAgent()
    
    # Sample question and context
    question = "What are the key ingredients in this product?"
    context = {
        "product": {
            "page_content": "This moisturizer contains Hyaluronic Acid, Niacinamide, and Ceramides. It's suitable for all skin types.",
            "metadata": {
                "product": "Daily Moisturizer",
                "brand": "SkinCare Co"
            }
        },
        "user_information": {
            "skin_type": "combination",
            "skin_issues": ["dryness"]
        }
    }
    
    print("Starting streaming test...\n")
    
    # Process the stream
    async for chunk in agent.process(question, context):
        if chunk["type"] == "content":
            print(f"Content chunk: {chunk['content']}")
        elif chunk["type"] == "citation":
            print(f"Citation: {chunk['citation']}")
        elif chunk["type"] == "error":
            print(f"Error: {chunk['content']}")
        elif chunk["type"] == "complete":
            print("\nStreaming complete!")

if __name__ == "__main__":
    asyncio.run(test_streaming()) 