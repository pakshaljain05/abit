import streamlit as st
from dotenv import load_dotenv
import pandas as pd
load_dotenv() ##load all the nevironment variables
import os
import requests
import threading
import time
# from extract_transcriptions import *
# from generate_summary import *
# from generate_similarity import *
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## getting the summary based on Prompt from Google Gemini Pro


def generate_gemini_content(transcript_text,prompt):

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text


def long_running_task():
    for i in range(10):
        # Simulate some computation
        time.sleep(1)
        st.write(f"Task is running... Step {i+1}")


prompt = """Act like you are a professional Content Strategeist/Analyst. Given a video summary analyze the content and give us a brief overview of what 
            the video is about under 50-100 words. Extract key insights and suggest some creative actionable content ideas for creators
            with similar niche. This is the provided summary : """


# prompt = """

# 1. Trend Analysis:
# Based on the transcriptions of videos, identify emerging trends or popular topics in the industry. 
# Analyze the recurring keywords and themes to uncover insights into current trends. 
# Provide recommendations on content topics that are gaining traction and may resonate well with their audience.

# 3. Audience Engagement Analysis Prompt:
# Extract insights from the transcriptions of videos regarding audience engagement strategies. 
# Identify patterns associated with high audience engagement, such as emotional language, interactive elements, or compelling storytelling techniques. 
# Provide recommendations for enhancing audience engagement based on these insights.

# 4. Content Format Experimentation Prompt:
# Explore the transcriptions of videos to identify unique content formats or narrative structures. 
# Analyze the storytelling techniques, presentation styles, and content formats that set videos apart. 
# Suggest experimental content formats or storytelling approaches that someone with similar niche can adopt to differentiate their videos and captivate their audience.

# 5. Keyword and Tag Analysis Prompt:
# Extract keywords and tags from the transcriptions of videos to understand the topics and concepts they focus on. 
# Analyze the language used in the transcriptions to identify relevant keywords and phrases. 
# Provide recommendations for optimizing video metadata, including titles, descriptions, and tags, to improve search visibility and discoverability.

# 6. Audience Feedback Analysis Prompt:
# Analyze audience sentiments expressed in the transcriptions of videos using sentiment analysis techniques. 
# Identify common feedback themes, positive/negative sentiments, and audience reactions to content. 
# Provide insights for genrating content ideas on audience preferences, sentiment trends, and potential pain points. 

# Use the above insights to inform content strategy decisions and enhance audience satisfaction from provided video title and content transcription of popular videos.
# Rely strictly on the provided text, without including external information.
# You can skip any part if there is not enough evidence to claim from the provided video title and video transcription :

# """

st.title("YouTube Video Recommendation")
user_channel_name = st.text_input("Enter your youtube channel name : ")
competitors_channel_names = st.text_input("Enter competitors channel names separated by commas : ")
input_list = competitors_channel_names.split(',')
competitors_channel_names = [name.strip() for name in input_list]

if st.button("Get Summaries"):
    if user_channel_name:
        try:
            df=pd.read_csv(f"data\interim\{user_channel_name}_video_recommended.csv")
            video_titles=df['video_title'].to_list()
            video_summary=df['summary'].to_list()
            channel_names=df['channel_name'].to_list()

            total_views=df['total_views'].to_list()
            published_date=df['publish_time'].to_list()
            st.write(f"Top recommended videos are given below :")
            # responses=[]
            # for i in range(len(video_summary[:1])):
            #     response = generate_gemini_content(video_summary[i], prompt)
            #     responses.append(response)
            # st.write(f"Top recommended videos are given below")

            # response1 = generate_gemini_content(video_summary[0], prompt)
            # st.write(f"{video_titles[0]} from {channel_names[0]}")
            # st.write(response1)
            for i in range(len(video_titles)):
                response = generate_gemini_content(video_summary[i], prompt)
                st.write(f"{video_titles[i]} from {channel_names[i]} published {published_date[i]} have about {total_views[i]}")
                # st.write(f"{video_titles[i]} from {channel_names[i]}")
                st.write(response)
                # st.write("Video Overview :")
                # st.write(response)
 
                # if st.button("Next"):
                #     st.write(response)
                # if transcript_text:
                #     summary = generate_gemini_content(transcript_text, prompt)
                #     st.markdown("## Detailed Notes:")
                #     st.write(summary)
                # else:
                #     st.write("Transcript not available for this video.")

        except Exception as e:
            st.write(f"Error: {e}")
    else:
        st.write("Please enter a valid YouTube Channel ID.")


# import time

# if st.button("Get Summaries"):
#     if user_channel_name:
#         try:
#             df = pd.read_csv(f"data\interim\{user_channel_name}_video_recommended.csv")
#             video_titles = df['video_title'].to_list()
#             video_summary = df['summary'].to_list()
#             channel_names = df['channel_name'].to_list()

#             st.write("Top recommended videos are given below")

#             # Store responses for all videos in a list
#             responses = [generate_gemini_content(summary, prompt) for summary in video_summary[:2]]

#             # Display first video summary
#             # current_video_index = 0
#             # st.write(f"{video_titles[current_video_index]} from {channel_names[current_video_index]}")
#             # st.write(responses[current_video_index])
#             # count=0
#             # # Button to display next video summary
#             # while current_video_index < len(video_titles) - 1:
#             #     count+=1
#             #     button_key = f"button_{count}"
#             #     if st.button(f"Next", key=button_key):
#             #         current_video_index += 1
#             #         st.write(f"{video_titles[current_video_index]} from {channel_names[current_video_index]}")
#             #         st.write(responses[current_video_index])

#             option = st.selectbox(
#                                 'How would you like to be contacted?',
#                                  ('Email', 'Home phone', 'Mobile phone'))

#             st.write('You selected:', option)

#         except Exception as e:
#             st.write(f"Error: {e}")
#     else:
#         st.write("Please enter a valid YouTube Channel ID.")


'''
check the prompts for restricting anything othr than the video details example sponsored content

'''
