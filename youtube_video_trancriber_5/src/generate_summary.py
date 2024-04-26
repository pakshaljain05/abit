from dotenv import load_dotenv

load_dotenv() ##load all the nevironment variables
import os
import google.generativeai as genai
import time,json
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import pandas as pd
# from youtube_api import YoutubeDataApi

# from extract_transcriptions import *

def configure_apikey():

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    print('Configuring Google API Key...')

def get_prompt():
    prompt = '''You are Professional Yotube video summarizer. Create a concise and comprehensive summary of the provided 
                video transcription text while adhering to these guidelines:

            Craft a summary that is detailed, thorough, in-depth, and complex, while maintaining clarity and conciseness.
            Incorporate main ideas and essential information, eliminating extraneous language and focusing on critical aspects
            of what the video is about.
            Rely strictly on the provided text, without including external information.
            Format the summary in paragraph form for easy understanding.
            Please provide the summary in under 200 words preferably 150 words of the text given here:'''
    
    return prompt

def load_model():
    safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    }
    ]
    model = genai.GenerativeModel("gemini-pro",safety_settings=safety_settings)

    return model

# def generate_gemini_content(transcript_text,prompt):

#     # model = genai.GenerativeModel("gemini-pro",safety_settings=safety_settings)
#     response = model.generate_content(prompt + transcript_text)
#     return response.text

def add_features(df):
    df['character_count']=df['transcripts'].str.len()
    df['word_count']=df['transcripts'].str.split().apply(len)
    transcript_lists=df['transcripts'].to_list()
    return transcript_lists

def summary_generation(df):
    # response_json=[]
    summary_list=[]
    # tag_list=[]
    # overview=[]
    # summary_error_list=[]
    transcript_lists=add_features(df)
    prompt = get_prompt()
    model = load_model()
    print(f'Summarizing {len(transcript_lists)} videos...')
    # start=time.time()
    for ind,transcript in enumerate(transcript_lists):
        print(ind)
        try:
            if transcript!='No Transcript':
                response=model.generate_content(prompt + transcript)
                response=response.text
                # print('Content summarized')
                # response=json.loads(response.replace('\n',''))
                # print('Output in json format')
                # summary_list.append(response['summary'])
                summary_list.append(response)

                # tag_list.append(response['tags'])
                # overview.append(response['brief'])
                # response_json.append(response)
            else:
                summary_list.append('None')
                # tag_list.append('None')
                # overview.append('None')
                # response_json.append('None')

        except Exception as e:
            print(e)
            print(f'Error at video id : {df.iloc[ind,1]}')
            print(f'Error at : {df.iloc[ind,2]}')

            # summary_error_list.append(df.iloc[ind,1])
            summary_list.append('None')
            # tag_list.append('None')
            # overview.append('None')
            # response_json.append('None')

    df['summary'] = summary_list
    # df['tags'] = tag_list
    # df['overview'] = overview
    df=df.iloc[:,1:]
    df=df.drop('transcripts',axis=1)
    print(df)
    return df

def main(user , non_user):
    user_channel_name = None
    competitors_channel_names = None
    transcript_path = 'data\\transcripts_data\\'
    summary_path = 'data\\summary_data\\'
    # if user:
    user_channel_name = input("Enter your youtube channel name : ")
    # if non_user:
    # competitors_channel_names = input("Enter competitors channel names separated by commas : ")
    # input_list = competitors_channel_names.split(',')
    # competitors_channel_names = [name.strip() for name in input_list]
    configure_apikey()

    if user:
        user_df = pd.read_csv(f'{transcript_path}{user_channel_name}_transcripts.csv',index_col=False)
        print('Extracting insights from competitors video...')

        user_summary_df=summary_generation(user_df,user,non_user)
        user_summary_df.to_csv(f"{summary_path}{user_channel_name}_summary.csv")



    if non_user:
        competitors_df = pd.read_csv(f'{transcript_path}{user_channel_name}_competitors_transcritpts.csv',index_col=False)
        print('Extracting insights from competitors video...')

        non_user_summary_df=summary_generation(competitors_df)
        non_user_summary_df.to_csv(f"{summary_path}{user_channel_name}_competitors_summary.csv")


    
    

main(user=False,non_user= True)
# df.to_csv('the_armchair_historian_summary.csv')