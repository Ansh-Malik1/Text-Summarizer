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
    Provide the summary of the following content in 300 words:
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
                if "youtube.com" in input_url:
                    loader=YoutubeLoader.from_youtube_url(input_url,add_video_info=True)
                else:
                    loader=UnstructuredURLLoader(urls=[input_url],ssl_verify=False,
                                                 headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"})
                docs=loader.load()

                chain=load_summarize_chain(llm,chain_type="stuff",prompt=prompt)
                output_summary=chain.run(docs)
                
                st.success(output_summary)  
        except Exception as e:
            st.exception(e)        