from dotenv import load_dotenv

load_dotenv() ##load all the nevironment variables
import os
# from googleapiclient import build
import requests
import json
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import pandas as pd
import scrapetube
import time

channel_name = input()                        # user input 
# youtube_api_key = os.getenv("YOUTUBE_API_KEY")

# def get_channel_id(channel_name,youtube_api_key):
#     try:
#         channel_id=requests.get(f'https://www.googleapis.com/youtube/v3/search?part=id&q={channel_name}&type=channel&key={youtube_api_key}').json()['items'][0]['id']['channelId']
#     except Exception as e:
#         print(e)
#     return channel_id
def scrape_videos(channel_name, sort_by, limit):
    error_video_lists=[]
    x=[]
    y=['video_id','video_title','publish_time','total_views']
    videos = scrapetube.get_channel(  
        # channel_id = channel_id,
        # channel_url: str = None,
        channel_username = channel_name,
        limit = limit,             # set limit 10 to competitors videoids change the filter too 
        sleep = 1,
        # proxies: dict = None,
        sort_by = sort_by
        # sort_by = "newest",                  #     Literal["newest", "oldest", "popular"]
        content_type = "videos"   #    Literal["videos", "shorts", "streams"]
        )

    for video in videos:
    
    
        video_id=video['videoId']
        video_title=video['title']['runs'][0]['text']
        # print(video_title)
        publish_time=video['publishedTimeText']['simpleText']
        try:
            total_views=video['viewCountText']['simpleText']
        except:
            print(video_title)
            error_video_lists.append(video_title)

            total_views = 'PREMIUM'
        x.append([video_id,video_title,publish_time,total_views])

    video_df=pd.DataFrame(data=x,columns=y)
    return video_df

def view_split(x):
    x=int(x.split(' ')[0].replace(',',''))
    return x

def video_preprocessing(video_df):
    video_df=video_df.drop_duplicates(['video_id'],keep='first').reset_index(drop=True)
    video_df['view_count']=video_df['total_views'].apply(view_split)
    video_ids=video_df['video_id'].to_list()
    return video_ids

def extract_transcript_details(video_ids):
    transcript_list=[]
    errors_list=[]
    for video_id in video_ids:
        try:
            transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

            transcript = ""
            for i in transcript_text:
                transcript += " " + i["text"]

            transcript_list.append(transcript)
            # return transcript

        except Exception as e:
            print(e)
            transcript_list.append('No Transcript')
            print(video_id)
            errors_list.append(video_id)
    return transcript_list

            # pass
        # raise e

# transcripts_list = extract_transcript_details(video_ids)
# video_df['transcript'] = transcripts_list
# video_df.to_csv(f'data\\transcripts_data\{channel_name}_transcripts.csv')
