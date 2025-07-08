import streamlit as st
import docx
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
import time
import os
from groq import Groq
import ollama

st.title("Meeting Summarizer")
st.subheader("Summarized Meeting Transcript:")

doc = docx.Document("./data/Meet01.docx")
full_text = [para.text for para in doc.paragraphs]
text = "\n".join(full_text)

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
system_prompt = 'Your goal is to summarize the text given to you in roughly 300 words. It is from a meeting between one or more people. Only output the summary without any additional text. Focus on providing a summary in freeform text with what people said and the action items coming out of it.'


OLLAMA_PROMPT = f"{system_prompt}: {text}"
OLLAMA_DATA = {
    "model": "llama3.1:latest",
    "prompt": OLLAMA_PROMPT,
    "stream": False,
    "keep_alive": "1m",
}


# Prompt template
prompt_template = f"""
ROLE
You are a clear-thinking, detail-oriented meeting assistant.

OBJECTIVE
Help me generate a comprehensive, actionable summary of the following meeting transcript.

CONTEXT PACKAGE
Audience: Team members and stakeholders who did not attend the meeting.
Voice and tone: Professional, clear, and concise.
Length target: 3-5 paragraphs or bullet points as needed.
Key facts, excerpts, data or links the answer must use:
1. [Paste or summarize the meeting transcript below]
Known constraints or boundaries: 
- Only use information present in the transcript.
- Avoid personal opinions or assumptions.
- Use the Cornell Notes technique for structure.
- Highlight participants, key topics, decisions, action items (with responsible persons), and unresolved issues.

WORKFLOW
1. Identify and list all participants, including their names and roles if mentioned.
2. Outline the meeting using the Cornell Notes technique:
   - Key topics and questions discussed
   - Main ideas and decisions made
   - Action items and who is responsible for each
   - Any follow-up points or unresolved issues
3. Translate the summary into clear, professional English.
4. Return the summary in plain text or bullet points.

CONTEXT-HANDLING RULES
If the transcript exceeds 2000 words, first give a one-sentence summary and ask whether to continue with the full summary.
If you need external knowledge not present in the transcript, list the missing points at the end.

OUTPUT FORMAT
Return all content in plain text or bullet lists only. When quoting a key fact, reference it by its position in the transcript if possible.

FIRST ACTION
Start with Workflow step 1: Identify and list all participants.

MEETING TRANSCRIPT:
{text}
"""

if st.button("Summarize with Ollama"):
    with st.spinner("Generating summary..."):
        response = requests.post(OLLAMA_ENDPOINT, json=OLLAMA_DATA)
        # print(response.json()["response"])
        st.write(response.json()["response"])
        # user_prompt = "Summarize this meeting transcript: " + text
        # response = ollama.chat(
        #     model='llama3.2:latest',  # or any model you have pulled with Ollama
        #     messages=[{'role': 'user', 'content': user_prompt}]
        # )
        # st.subheader("Summary")
        # st.write(response['message']['content'])
    



# def hf_summarize(prompt):
#     payload = {"inputs": prompt}
#     response = requests.post(API_URL, headers=headers, json=payload)
#     try:
#         return response.json()[0]['summary_text']
#     except Exception as e:
#         return f"Error: {response.text}"


# def split_text(text, chunk_size=900, chunk_overlap=100):
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=chunk_size,
#         chunk_overlap=chunk_overlap,
#         separators=["\n\n", "\n", ".", "!", "?", " "]
#     )
#     return splitter.split_text(text)
# if text.strip():
#         # Split text into manageable chunks
#         chunks = split_text(text)
#         summaries = []
#         progress_bar = st.progress(0)
#         with st.spinner("Summarizing..."):
#             for i, chunk in enumerate(chunks):
                
                
# chat_completion = client.chat.completions.create(
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": prompt,
#                     }
#                 ],
#                 model="gemma2-9b-it",
#                 stream=False,
#                 )
#                 print(chat_completion.choices[0].message.content)
#                 summary = chat_completion.choices[0].message.content
#                 summaries.append(summary)
#                 progress_bar.progress((i + 1) / len(chunks))
#             progress_bar.progress(100)
#         final_summary = "\n\n".join(summaries)
#         st.subheader("Summary")
#         st.write(final_summary)

# if st.button("Summarize"):
#     client = Groq(
#     api_key="",
#     )
#     prompt = prompt_template.format(text=text)
#     response = ollama.chat(
#         model='llama3',  # or any model you have pulled with Ollama
#         messages=[{'role': 'user', 'content': prompt]}]
#     )
#     st.subheader("Summary")
#     st.write(response['message']['content'])
#     # Use Groq for summarization