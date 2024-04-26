import streamlit as st
from dotenv import load_dotenv

load_dotenv() ##load all the nevironment variables
import os
import google.generativeai as genai

from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are Yotube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """

## getting the transcript data from yt videos
def extract_transcript_details(video_id):
    try:
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except Exception as e:
        raise e

## getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text,prompt):

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

## Function to get the top 5 recent videos from a channel
def get_top_5_recent_videos(channel_id):
    youtube = build('youtube', 'v3', developerKey=os.getenv("YOUTUBE_API_KEY"))

    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        order="date",
        type="video",
        maxResults=5
    )

    response = request.execute()

    video_ids = [item['id']['videoId'] for item in response['items']]

    return video_ids

st.title("YouTube Channel Video Summarizer")
channel_id = st.text_input("Enter YouTube Channel ID:")

if st.button("Get Summaries"):
    if channel_id:
        try:
            video_ids = get_top_5_recent_videos(channel_id)

            for video_id in video_ids:
                st.write(f"Summary for Video ID: {video_id}")
                transcript_text = extract_transcript_details(video_id)
                if transcript_text:
                    summary = generate_gemini_content(transcript_text, prompt)
                    st.markdown("## Detailed Notes:")
                    st.write(summary)
                else:
                    st.write("Transcript not available for this video.")

        except Exception as e:
            st.write(f"Error: {str(e)}")
    else:
        st.write("Please enter a valid YouTube Channel ID.")
