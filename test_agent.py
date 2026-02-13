from langchain.agents import initialize_agent, Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Your LLM setup ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# --- Define tools ---
def calculator(expression: str) -> str:
    """Evaluate a math expression."""
    return str(eval(expression))

tools = [
    Tool(
        name="Calculator",
        func=calculator,
        description="Useful for evaluating math expressions"
    )
]

# --- Create the agent ---
agent = initialize_agent(
    tools,
    llm,
    agent="chat-conversational-react-description",  # recommended type
    verbose=True
)

# --- Run the agent ---
result = agent.run("What is 42 * 17?")
print(result)
