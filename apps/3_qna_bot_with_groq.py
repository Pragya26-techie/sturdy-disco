# LLM
# Tool - Google SEARCH Tool
# Agent
# Memory
## web interface


from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
import streamlit as st

llm = ChatGroq(model="openai/gpt-oss-20b",streaming = True)
search = GoogleSerperAPIWrapper()
tool = [search.run]

if "memory" not in st.session_state:   #if memory object id does not exixst in seesion_state then only create new one
    st.session_state.memory = InMemorySaver() #session state create one memory object and hold it till the server is running
# memory = InMemorySaver()-->recreate memory object on every execution,model loss its convo flow
    st.session_state.history = []


agent = create_agent(
    model = llm,
    tools = tool,
    checkpointer=st.session_state.memory,
    system_prompt = "you are amazing ai agent and can search on google as well"
)

print(st.session_state.memory)

## Buidling Web Interface
st.subheader("QuickAnswer - Answers at the speed of thought")

# upoading store data on browser
for message in st.session_state.history:
    role = message["role"]
    content = message["content"]
    st.chat_message(role).markdown(content)

query = st.chat_input("Ask Anything ?")
if query:
    st.chat_message("user").markdown(query)
    st.session_state.history.append({"role":"user","content":query})

response = agent.stream(
    {"messages":[{"role":"user","content":query}]},
    {"configurable":{"thread_id":"1"}},
    stream_mode = "messages"
)   #invoke-->getting complete answer ek baar me

ai_container = st.chat_message("ai")
with ai_container:
    space = st.empty()
    message = ""

    for chunk in response:
        message = message + chunk[0].content
        space.write(message)

# answer = response["messages"][-1].content
# st.chat_message("ai").markdown(answer)
st.session_state.history.append({"role":"ai","content":message})


