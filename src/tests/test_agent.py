# Simple agent with simple tool

import os
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

api_key = os.getenv("GEMINI_API_KEY") # change accordingly

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.6,
    google_api_key=api_key
)

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model=llm,
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

# Run the agent
agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)