import streamlit as st
import os
import fitz  # PyMuPDF
import requests
import base64

# ⬅️ Back button
if st.button("⬅️ Back to Home"):
    st.switch_page("Home.py")

st.set_page_config(page_title="Summarize Meeting", layout="wide")
st.title("📝 Meeting Summarizer")

# 🔒 Check if user came from homepage
if "selected_meeting" not in st.session_state:
    st.error("No meeting selected. Please return to the home page.")
    st.stop()

# 📄 Get selected PDF
meeting_file = st.session_state["selected_meeting"]
transcript_path = os.path.join("data/Meetings", meeting_file)
current_meeting = meeting_file

# Clear state only if it's a new meeting file
if st.session_state.get("last_summary_meeting") != current_meeting:
    st.session_state["summary"] = ""
    st.session_state["chat_history"] = []
    st.session_state["last_summary_meeting"] = current_meeting

label = meeting_file.replace(".pdf", "")
st.subheader(f"Summarizing: {label}")

with open(transcript_path, "rb") as f:
    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="300" height="500" type="application/pdf"></iframe>'
st.sidebar.markdown("### 📄 Meeting PDF")
st.sidebar.markdown(pdf_display, unsafe_allow_html=True)

# 📜 Extract text from PDF
@st.cache_data
def extract_text_from_pdf(path):
    doc = fitz.open(path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text.strip()

transcript_text = extract_text_from_pdf(transcript_path)
word_count = len(transcript_text.split())

# 🌐 Session state for summary and chat
if "summary" not in st.session_state:
    st.session_state["summary"] = ""
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# 🖌️ Custom styling
st.markdown("""
    <style>
    .button-style {
        display: inline-block;
        padding: 1em 2em;
        margin: 0.5em 0;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 12px;
        width: 100%;
        transition: 0.3s ease-in-out;
    }
    .button-style:hover {
        background-color: #45a049;
        transform: scale(1.03);
        cursor: pointer;
    }
    .stTextArea textarea {
        font-size: 16px !important;
        line-height: 1.6 !important;
    }
    [data-testid="stSidebar"] {
            min-width: 400px;
            max-width: 400px;
            width: 400px;
        }
    </style>
""", unsafe_allow_html=True)

# 🔍 Expandable view of full transcript
with st.expander("📄 View full transcript"):
    st.text_area("Transcript", transcript_text, height=300)

# 🚀 Run summarization
if st.button("🧠 Summarize", type="primary"):
    with st.spinner("Generating summary..."):
            prompt = f"""
You are a clear-thinking, detail-oriented meeting assistant. You're a professional assistant. You do not apologize. Always provide your best answer, even with long or imperfect inputs.

OBJECTIVE:
Help generate a professional summary of this transcript for absent team members.

CONSTRAINTS:
- Use Cornell Notes structure.
- Include participants, key topics, decisions, action items (with persons), and unresolved issues.
- Use only info from the transcript. No opinions. No outside facts.

FORMAT:
- Bullet points or short paragraphs.
- Plain text only. No Markdown.

TRANSCRIPT:
{transcript_text}
"""
            payload = {
                "model": "llama3.1:latest",
                "model_config": {
                    "max_tokens": 1000,
                    "temperature": 0.5,
                    "top_p": 0.9,
                },
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }

            try:
                response = requests.post("http://localhost:11434/api/chat", json=payload)
                if response.status_code == 200:
                    st.session_state["summary"] = response.json().get("message", {}).get("content", "")
                else:
                    st.error("⚠️ Ollama inference failed.")
            except Exception as e:
                st.error(f"⚠️ Error contacting Ollama: {e}")

# 🧾 Show summary
if st.session_state["summary"]:
    st.subheader("✅ Summary")
    st.markdown(st.session_state["summary"])

    # 💬 Chat Interface
    st.markdown("---")
    st.subheader("🤖 Chat with the AI about this meeting")

    for entry in st.session_state.chat_history:
        with st.chat_message(entry["role"]):
            st.markdown(entry["content"])

    user_input = st.chat_input("Ask a question about the meeting...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            chat_prompt = f"""
You're a helpful assistant. Answer based only on the transcript below.

TRANSCRIPT:
\"\"\"
{transcript_text}
\"\"\"

QUESTION:
{user_input}
"""

            chat_payload = {
                "model": "llama3.1:latest",
                "messages": [{"role": "user", "content": chat_prompt}],
                "stream": False
            }

            try:
                response = requests.post("http://localhost:11434/api/chat", json=chat_payload)
                if response.status_code == 200:
                    reply = response.json().get("message", {}).get("content", "")
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    with st.chat_message("assistant"):
                        st.markdown(reply)
                else:
                    st.error("⚠️ Ollama failed to generate a response.")
            except Exception as e:
                st.error(f"⚠️ Error contacting Ollama: {e}")








# import streamlit as st
# import docx
# import requests
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# import time
# import os
# from groq import Groq
# import ollama

# st.title("Meeting Summarizer")
# st.subheader("Summarized Meeting Transcript:")

# doc = docx.Document("./data/Meet01.docx")
# full_text = [para.text for para in doc.paragraphs]
# text = "\n".join(full_text)

# OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
# system_prompt = 'Your goal is to summarize the text given to you in roughly 300 words. It is from a meeting between one or more people. Only output the summary without any additional text. Focus on providing a summary in freeform text with what people said and the action items coming out of it.'


# OLLAMA_PROMPT = f"{system_prompt}: {text}"
# OLLAMA_DATA = {
#     "model": "llama3.1:latest",
#     "prompt": OLLAMA_PROMPT,
#     "stream": False,
#     "keep_alive": "1m",
# }


# ollama_url = "http://172.21.240.1:11434/api/chat"




# # Prompt template
#         prompt = f"""
# ROLE
# You are a clear-thinking, detail-oriented meeting assistant.

# OBJECTIVE
# Help me generate a comprehensive, actionable summary of the following meeting transcript.

# CONTEXT PACKAGE
# Audience: Team members and stakeholders who did not attend the meeting.
# Voice and tone: Professional, clear, and concise.
# Length target: 3-5 paragraphs or bullet points as needed.
# Key facts, excerpts, data or links the answer must use:
# 1. [Paste or summarize the meeting transcript below]
# Known constraints or boundaries: 
# - Only use information present in the transcript.
# - Avoid personal opinions or assumptions.
# - Use the Cornell Notes technique for structure.
# - Highlight participants, key topics, decisions, action items (with responsible persons), and unresolved issues.

# WORKFLOW
# 1. Identify and list all participants, including their names and roles if mentioned.
# 2. Outline the meeting using the Cornell Notes technique:
#    - Key topics and questions discussed
#    - Main ideas and decisions made
#    - Action items and who is responsible for each
#    - Any follow-up points or unresolved issues
# 3. Translate the summary into clear, professional English.
# 4. Return the summary in plain text or bullet points.

# CONTEXT-HANDLING RULES
# If the transcript exceeds 2000 words, first give a one-sentence summary and ask whether to continue with the full summary.
# If you need external knowledge not present in the transcript, list the missing points at the end.

# OUTPUT FORMAT
# Return all content in plain text or bullet lists only. When quoting a key fact, reference it by its position in the transcript if possible.

# FIRST ACTION
# Start with Workflow step 1: Identify and list all participants.

# MEETING TRANSCRIPT:
# {transcript_text}
# """

# if st.button("Summarize with Ollama"):
#     with st.spinner("Generating summary..."):
#         response = requests.post(OLLAMA_ENDPOINT, json=OLLAMA_DATA)
#         # print(response.json()["response"])
#         payload = {
#         "model": "llama3.1:latest",
#         "messages": [{"role": "user", "content": OLLAMA_PROMPT}]
#         }
#         ollama_url = "http://localhost:11435/api/chat"
#         response = requests.post(ollama_url, json=payload)
#         st.write(response.json()["response"])
#         # user_prompt = "Summarize this meeting transcript: " + text
#         # response = ollama.chat(
#         #     model='llama3.2:latest',  # or any model you have pulled with Ollama
#         #     messages=[{'role': 'user', 'content': user_prompt}]
#         # )
#         # st.subheader("Summary")
#         # st.write(response['message']['content'])
    



# # def hf_summarize(prompt):
# #     payload = {"inputs": prompt}
# #     response = requests.post(API_URL, headers=headers, json=payload)
# #     try:
# #         return response.json()[0]['summary_text']
# #     except Exception as e:
# #         return f"Error: {response.text}"


# # def split_text(text, chunk_size=900, chunk_overlap=100):
# #     splitter = RecursiveCharacterTextSplitter(
# #         chunk_size=chunk_size,
# #         chunk_overlap=chunk_overlap,
# #         separators=["\n\n", "\n", ".", "!", "?", " "]
# #     )
# #     return splitter.split_text(text)
# # if text.strip():
# #         # Split text into manageable chunks
# #         chunks = split_text(text)
# #         summaries = []
# #         progress_bar = st.progress(0)
# #         with st.spinner("Summarizing..."):
# #             for i, chunk in enumerate(chunks):
                
                
# # chat_completion = client.chat.completions.create(
# #                 messages=[
# #                     {
# #                         "role": "user",
# #                         "content": prompt,
# #                     }
# #                 ],
# #                 model="gemma2-9b-it",
# #                 stream=False,
# #                 )
# #                 print(chat_completion.choices[0].message.content)
# #                 summary = chat_completion.choices[0].message.content
# #                 summaries.append(summary)
# #                 progress_bar.progress((i + 1) / len(chunks))
# #             progress_bar.progress(100)
# #         final_summary = "\n\n".join(summaries)
# #         st.subheader("Summary")
# #         st.write(final_summary)

# # if st.button("Summarize"):
# #     client = Groq(
# #     api_key="",
# #     )
# #     prompt = prompt_template.format(text=text)
# #     response = ollama.chat(
# #         model='llama3',  # or any model you have pulled with Ollama
# #         messages=[{'role': 'user', 'content': prompt]}]
# #     )
# #     st.subheader("Summary")
# #     st.write(response['message']['content'])
# #     # Use Groq for summarization