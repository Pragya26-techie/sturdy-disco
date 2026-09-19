from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
st.title("PuchhoMitr:AI QnA Bot")
st.markdown("My QnA Bot with LangChain and google Gemini !")
# while True:
#     query = input("User")
#     if query.lower() in ["quit","exit","bye"]:
#         print("GoodBye")
#     result = llm.invoke(query)
#     print("AI:",result.text,"\n") ## .content printing only refined output

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    st.chat_message(role).markdown(content)

query = st.chat_input("Ask anything..")
if query:
    st.session_state.messages.append({"role":"user","content":query})
    st.chat_message("user").markdown(query)
    res = llm.invoke(query)
    st.chat_message("ai").markdown(res.text)
    st.session_state.messages.append({"role":"ai","content":res.text})

