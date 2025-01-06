import streamlit as st
import validators
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader,UnstructuredURLLoader
from youtube_transcript_api import YouTubeTranscriptApi
import re

def extract_video_id(url):
    pattern = r"v=([a-zA-Z0-9_-]+)|youtu\.be/([a-zA-Z0-9_-]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1) or match.group(2)
    return None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([item["text"] for item in transcript])
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None
    
    
st.set_page_config(page_title="Langchain : Summarize text from YT or website")
st.title("Langchain : Summarize text from YT or website")
st.subheader("Summarize URL")

with st.sidebar:
    groq_api_key=st.text_input("Enter your GROQ API key here",type="password",value="")
    
input_url = st.text_input("URL",label_visibility="collapsed")

if st.button("Summarize content"):
    llm=ChatGroq(model="Gemma2-9b-it",api_key=groq_api_key)
    
    prompt_template="""
    Provide the summary of the following content in 350 words.
    Context:{text}
    """
    prompt=PromptTemplate(template=prompt_template,input_variables=["text"])
    
    if not groq_api_key.strip() or not input_url.strip():
        st.error("Please enter both GROQ API key and URL")
    elif not validators.url(input_url):
        st.error("Please enter a valid URL")
    
    else:
        try:
            with st.spinner("Waiting..."):
                video_id = input_url.split("=")[1]
                transcript_text=YouTubeTranscriptApi.get_transcript(video_id)
                transcript=""
                for i in transcript_text:
                    transcript+=" "+i["text"]

                chain=prompt|llm
                output=chain.invoke(transcript)
                summary=output.content
                
                st.success(summary)  
        except Exception as e:
            st.exception(e)