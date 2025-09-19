import streamlit as st
import os
import fitz  # PyMuPDF
import requests
import base64
from vector_db import get_vector_db, retrieve_relevant_context

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

# Check if this meeting is in the vector database
vector_db = get_vector_db()
if vector_db and meeting_file in vector_db.get_all_filenames():
    st.success("✅ Meeting indexed for smart retrieval")
else:
    st.warning("⚠️ Meeting not yet indexed - using full transcript for chat")

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

# Dictionary of button labels and their corresponding prompts
# Note: Summaries use full transcript for completeness, but chat uses vector retrieval for efficiency
summarization_options = {
    "📝 Cornell Notes": """
You are a meeting assistant. Create a Cornell Notes summary immediately.

STRICT INSTRUCTIONS:
- Do NOT comment on text length or complexity
- Do NOT use phrases like "I'm sorry", "appears to", "seems like"
- Start IMMEDIATELY with the Cornell Notes format
- Use ONLY information from the transcript

FORMAT (follow exactly):
PARTICIPANTS:
• [List each person and their role]

NOTES:
• [Key discussion points]
• [Important decisions made]
• [Technical details discussed]

CUES:
• [Main topics/keywords]
• [Action items]
• [Deadlines mentioned]

SUMMARY:
[2-3 sentences covering the main outcomes and next steps]

LANGUAGE: Always respond in the language of the transcript.

TRANSCRIPT:
{transcript_text}
""",
    
    "📝 1 to 1 Meeting": """
You are an expert in meeting notes. I am having a 1:1 meeting with someone in my team, please capture these meeting notes in a concise and actionable format. Focus on immediate priorities, progress, challenges, and personal feedback, ensuring the notes are structured for clarity, efficiency and easy follow-up. Please highlight key phrases and organize content hierarchically in the generated notes.

RULES:
- No preamble or explanatory text
- Start directly with the meeting content
- Focus on actionable items and feedback
- Organize hierarchically with clear structure
- Highlight key phrases

LANGUAGE: Always respond in the language of the transcript.

TRANSCRIPT:
{transcript_text}
""",
    
    "📋 Meeting Summary": """
Summarize given text into a well-formed meeting summary, and present the results using markdown format. Please highlight key phrases in the generated notes. Do not show results that cannot be generated.

RULES:
- Use markdown format for structure
- Highlight key phrases
- Present clear, well-formed summary
- Only include content that can be generated from the transcript

LANGUAGE: Always respond in the language of the transcript.

TRANSCRIPT:
{transcript_text}
""",
    
    "🧠 Feynman Tech": """
Turn the given text into a detailed study note using Feynman Technique to help the user to achieve a deep and intuitive understanding of the topic. The output should include a clear, simplified explanation of the topic, identification, and resolution of knowledge gaps, and a refined explanation that is ready for teaching. Each step should be documented thoroughly to ensure a comprehensive understanding. Please highlight key phrases and organize content hierarchically in the generated notes.

RULES:
- Apply Feynman Technique methodology
- Create detailed study notes for deep understanding
- Include simplified explanations and knowledge gap resolution
- Document each step thoroughly
- Highlight key phrases and organize hierarchically

LANGUAGE: Always respond in the language of the transcript.

TRANSCRIPT:
{transcript_text}
""",
    
    "� Project Sync": """
You are an expert in meeting notes. I participated in our project sync to get a clear picture of where we stand and what's coming up. My focus was on understanding our progress, identifying any hurdles, and ensuring we're all aligned on our next moves to keep things on track. Please highlight key phrases and organize content hierarchically in the generated notes.

RULES:
- Focus on project progress and alignment
- Identify hurdles and next steps
- Organize hierarchically with clear structure
- Highlight key phrases for easy reference

LANGUAGE: Always respond in the language of the transcript.

TRANSCRIPT:
{transcript_text}
""",
    
    "� Brainstorming": """
Summarize given text into a well-formed Brainstorm Notes, and present the results as follows use markdown format:
## Ideas 1
#### Key Concepts
#### Pros & Cons
#### Examples
## Ideas ...
#### Key Concepts
#### Pros & Cons
#### Examples
## Exploration
Please highlight key phrases and organize content hierarchically in the generated notes. Do not show results that cannot be generated.

RULES:
- Use the specified markdown format structure
- Organize ideas with key concepts, pros & cons, and examples
- Include exploration section
- Highlight key phrases
- Only show results that can be generated

LANGUAGE: Always respond in the language of the transcript.

TRANSCRIPT:
{transcript_text}
"""
}

# 🚀 Show initial summarization buttons ONLY if no summary has been generated yet
if not st.session_state["summary"]:
    st.subheader("🧠 Choose Summarization Style")
    
    # Create inline buttons with unique keys
    cols = st.columns(len(summarization_options))
    for i, (label, prompt_template) in enumerate(summarization_options.items()):
        with cols[i]:
            if st.button(label, type="secondary", use_container_width=True, key=f"initial_{i}"):
                with st.spinner(f"Generating {label.split(' ')[1]} summary..."):
                    prompt = prompt_template.format(transcript_text=transcript_text)
                    
                    payload = {
                        "model": "llama3.1:latest",
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False
                    }

                    try:
                        response = requests.post("http://localhost:11434/api/chat", json=payload)
                        if response.status_code == 200:
                            summary_content = response.json().get("message", {}).get("content", "")
                            
                            # Add summary to chat history as assistant message
                            st.session_state.chat_history.append({
                                "role": "assistant", 
                                "content": f"**{label}**\n\n{summary_content}",
                                "type": "summary"
                            })
                            
                            # Set the main summary for backward compatibility
                            st.session_state["summary"] = summary_content
                            st.session_state["summary_type"] = label
                            
                            st.rerun()  # Refresh to show new message
                        else:
                            st.error("⚠️ Ollama inference failed.")
                    except Exception as e:
                        st.error(f"⚠️ Error contacting Ollama: {e}")

# 💬 Chat Interface - show if there's any chat history or summary
if st.session_state["summary"] or st.session_state.chat_history:
    st.markdown("---")
    st.subheader("🤖 Chat with the AI about this meeting")

    # Display existing chat history (including summaries)
    for entry in st.session_state.chat_history:
        with st.chat_message(entry["role"]):
            st.markdown(entry["content"])

    user_input = st.chat_input("Ask a question about the meeting...")
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("Thinking..."):
            # Use vector database to retrieve relevant context instead of full transcript
            relevant_context = retrieve_relevant_context(user_input, meeting_file, top_k=3)
            
            chat_prompt = f"""
Answer the question directly based only on the relevant meeting content below. Do not use phrases like "based on the transcript" or "it appears". Start immediately with your answer.

RELEVANT MEETING CONTENT:
\"\"\"
{relevant_context}
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
                    # Display assistant response immediately
                    with st.chat_message("assistant"):
                        st.markdown(reply)
                else:
                    st.error("⚠️ Ollama failed to generate a response.")
            except Exception as e:
                st.error(f"⚠️ Error contacting Ollama: {e}")

# 🚀 Show summarization buttons at the END if a summary has been generated
if st.session_state.get("summary"):
    st.markdown("---")
    st.subheader("🧠 Generate Another Summary")
    
    # Create inline buttons with unique keys
    cols = st.columns(len(summarization_options))
    for i, (label, prompt_template) in enumerate(summarization_options.items()):
        with cols[i]:
            # Use unique keys to avoid button conflicts
            button_key = f"end_{i}_{len(st.session_state.chat_history)}"
            if st.button(label, type="secondary", use_container_width=True, key=button_key):
                with st.spinner(f"Generating {label.split(' ')[1]} summary..."):
                    prompt = prompt_template.format(transcript_text=transcript_text)
                    
                    payload = {
                        "model": "llama3.1:latest",
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False
                    }

                    try:
                        response = requests.post("http://localhost:11434/api/chat", json=payload)
                        if response.status_code == 200:
                            summary_content = response.json().get("message", {}).get("content", "")
                            
                            # Add summary to chat history as assistant message
                            st.session_state.chat_history.append({
                                "role": "assistant", 
                                "content": f"**{label}**\n\n{summary_content}",
                                "type": "summary"
                            })
                            
                            st.rerun()  # Refresh to show new message
                        else:
                            st.error("⚠️ Ollama inference failed.")
                    except Exception as e:
                        st.error(f"⚠️ Error contacting Ollama: {e}")
                        # Remove the expandable sections code completely



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