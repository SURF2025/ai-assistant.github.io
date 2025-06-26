# import streamlit as st
# from langchain.chat_models import ChatOllama
# from langchain.schema import HumanMessage, AIMessage
# from langchain.memory import ConversationBufferMemory
# from langchain.chains import LLMChain
# from langchain.prompts import PromptTemplate
# st.title("Summarize your meeings")
# st.write("Summarizer")


import streamlit as st
from langchain.llms import Ollama
from langchain_community.document_loaders import PyPDFLoader
import docx

# Load PDF document
# pdf_path = "example.pdf"  # Replace with your PDF file path 
# loader = PyPDFLoader(pdf_path)
# pages = loader.load()
st.title("Meeting Summarizer")
st.subheader("Summarized Meeting Transcript:")
doc = docx.Document("./data/Meet01.docx")
full_text = []
for para in doc.paragraphs:
    full_text.append(para.text)

text = "\n".join(full_text)

# Split documents into manageable chunks

# Initialize Ollama LLM via LangChain
# llm = Ollama(
#     base_url="http://localhost:11434",  # Default Ollama endpoint
#     model="llama3.1"
# )


prompt_template = """You are a helpful, meeting summarizing assistant. Summarize the following meeting transcript: {text}, along with an English translation of
the summary, using the Cornell Notes technique. Provide the summary in English. Make sure to expand upon each discussion point and provide a detailed summary of the meeting."""
# response = llm.invoke(prompt_template.format(text=text), temperature=0.65, max_tokens=2000)

# st.write(response)
# st.set_page_config(page_title="Llama 3.1 Chat", page_icon="🤖")
# st.title("💬 Llama 3.1 Chat (via Ollama & LangChain)")

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display chat history
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # User input
# if prompt := st.chat_input("Say something..."):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # Get Llama 3.1 response via LangChain
#     with st.spinner("Llama 3.1 is thinking..."):
#         response = llm(prompt)
#     st.session_state.messages.append({"role": "assistant", "content": response})
#     with st.chat_message("assistant"):
#         st.markdown(response)