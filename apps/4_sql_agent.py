# Buidling Task Manager with real-time database using sql

from dotenv import load_dotenv
load_dotenv()

### db,llm,tools,create_agent,syatem_prompt
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit #providing tools to llm based on which it can take action on user query
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
import streamlit as st #convert cli-appliaction into web interface

db = SQLDatabase.from_uri("sqlite:///my_tasks.db")
db.run("""
       CREATE TABLE IF NOT EXISTS tasks (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       title TEXT NOT NULL,
       description TEXT,
       status TEXT CHECK (status IN ('pending','in_progress','completed')) DEFAULT 'pending',
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       );
""")

## Create Agent-->llm,tools,memory,system_prompt

llm_model = ChatGroq(model="openai/gpt-oss-20b")
toolkit = SQLDatabaseToolkit(db=db,llm = llm_model)
tools = toolkit.get_tools()
# memory = InMemorySaver()->directly initialised inside function def_agent


sytem_prompt = system_prompt = """
you are a task manangement assistant that interacts with a SQL database contaning a 'tasks' table.

Task RULES:
1.Limit SELECT queries to 10 results max with ORDER BY created_at DESC
2.After CREATE/UPDATE/DELETE, confirm with SELECT query
3.If the user requests a list of tasks,present the output in a structured table format to ensure a clean and organized display in the browser."

CRUD OPERATIONS:
CREATE: INSERT INTO tasks(title,description,status)
READ:SELECT * FROM tasks WHERE..LIMIT 10
UPDATE:UPDATE tasks SET status=?WHERE id=? OR title=?
DELETE:DELETE FROM tasks WHERE id=? OR title=?

Table schema: id, title, description, status(pending/in_progress/completed), created_at.
"""

@st.cache_resource #->fn again and again run ni hona chaiye,create_agent fir recreate nhi hoga aur hamari memory refresh ni hogi to conv flow bna rhega
def get_agent():
    agent = create_agent(
    model = llm_model,
    tools = tools,
    checkpointer = InMemorySaver(),
    system_prompt = system_prompt
)
    return agent

agent = get_agent()

#building interface
st.subheader("TaskOps-Plan and manage your Tasks")
if "messages" not in st.session_state:
     st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

prompt = st.chat_input("Ask me to manage your tasks")

if prompt:
    st.chat_message("user").markdown(prompt) #showing user query on interface
    st.session_state.messages.append({"role":"user", "content":prompt})

    with st.chat_message("ai"):
       with st.spinner("Processing..."):   
        response = agent.invoke({"messages":[{"role":"user","content":prompt}]},{"configurable":{"thread_id":"1"}})

        result = response["messages"][-1].content
        st.markdown(result)
        st.session_state.messages.append({"role":"ai", "content":result})
    
    
    # print("AI: ",result)

# check avialable tool
# for tool in tools:
#     print(tool.name)

# print("DB Table Create Successfully")
