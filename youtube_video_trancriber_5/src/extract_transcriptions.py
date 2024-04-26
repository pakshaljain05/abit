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


# youtube_api_key = os.getenv("YOUTUBE_API_KEY")

# def get_channel_id(channel_name,youtube_api_key):
#     try:
#         channel_id=requests.get(f'https://www.googleapis.com/youtube/v3/search?part=id&q={channel_name}&type=channel&key={youtube_api_key}').json()['items'][0]['id']['channelId']
#     except Exception as e:
#         print(e)
#     return channel_id
def scrape_videos(channel_name):
    print(f"Collecting videos for {channel_name}...")
    error_video_lists=[]
    x=[]
    y=['video_id','video_title','publish_time','total_views']
    try: 
        videos = scrapetube.get_channel(  
            # channel_id = channel_id,
            # channel_url: str = None,
            channel_username = channel_name,
            # limit = limit,             # set limit 10 to competitors videoids change the filter too 
            sleep = 2,
            # proxies: dict = None,
            # sort_by = sort_by,
            sort_by = "newest",                  #     Literal["newest", "oldest", "popular"]
            content_type = "videos"   #    Literal["videos", "shorts", "streams"]
            )

        for video in videos:
        
            video_id=video['videoId']
            video_title=video['title']['runs'][0]['text']
            # print(video_title)
            publish_time=video['publishedTimeText']['simpleText']
            try:
                total_views=video['viewCountText']['simpleText']
                # print(video_id,video_title,publish_time,total_views)
            except:
                print(f'Issues in getting data for {video_title}')
                error_video_lists.append(video_title)

                total_views = 'PREMIUM'
            x.append([video_id,video_title,publish_time,total_views])
    except Exception as e:
        print(f'User not found for channel name {channel_name}')

    
    video_df=pd.DataFrame(data=x,columns=y)
    # print(video_df)
    return video_df

def view_split(x):
    x=int(x.split(' ')[0].replace(',',''))
    return x

def video_filter(df):
    condition = df['publish_time'] == '1 year ago'
    subset_df = df.loc[:condition.idxmax()]  # idxmax() returns the index of the first occurrence of True
    subset_df.sort_values(['view_count'],ascending=False).head(10)
    return subset_df


def video_preprocessing(df):

    df=df.drop_duplicates(['video_id'],keep='first').reset_index(drop=True)
    df['view_count']=df['total_views'].apply(view_split)
    return df

def video_concat(competitors_channel_names):
    print(f"Filtering all the competitors video ...")
    concat_df=pd.DataFrame(columns=['video_id', 'video_title', 'publish_time', 'total_views', 'view_count'])
    for name in competitors_channel_names:
        temp_df=video_preprocessing(scrape_videos(name))
        temp_df=video_filter(temp_df)
        # print(f'Total videos for {name} : ',len(temp))
        concat_df=pd.concat([concat_df,temp_df])
        # print(len(concat_df))
    return concat_df


def extract_transcript_details(df,get_transcript:bool):
    if get_transcript:
        print('Extracting transcriptions from videos...')
        video_ids=df['video_id'].to_list()
        video_title = df['video_title'].to_list()
        transcript_list=[]
        errors_list=[]
        for ind,video_id in enumerate(video_ids):
            try:
                transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

                transcript = ""
                for i in transcript_text:
                    transcript += " " + i["text"]

                transcript_list.append(transcript)
                # return transcript

            except Exception as e:
                print(f"No transcription for video : {video_title[ind]}")
                transcript_list.append('No Transcript')
                # print(video_id)
                errors_list.append(video_id)
        df['transcripts']=transcript_list

    return df

            # pass
        # raise e

# transcripts_list = extract_transcript_details(video_ids)
# video_df['transcript'] = transcripts_list
# video_df.to_csv(f'data\\transcripts_data\{channel_name}_transcripts.csv')

def final_data(user, non_user,user_channel_name, competitors_channel_names,transcript,path):
    try:
        if user and non_user:
            user_df=extract_transcript_details(video_preprocessing(scrape_videos(user_channel_name)),transcript)
            competitor_df = extract_transcript_details(video_concat(competitors_channel_names),transcript)
            # return user_df, competitor_df
        else:
            if user and not non_user:
                user_df=extract_transcript_details(video_preprocessing(scrape_videos(user_channel_name)),transcript)
                # return user_df
            else:
                competitor_df = extract_transcript_details(video_concat(competitors_channel_names),transcript)
                # return competitor_df
        
        if user:        
            user_df.to_csv(f'{path}{user_channel_name}_data.csv')
        if non_user:
            competitor_df.to_csv(f'{path}{user_channel_name}_competitors_data.csv')
    except Exception as e:
        print(e)



def main(user , non_user , transcript=False):
    user_channel_name = None
    competitors_channel_names = None
    if transcript:
        path = 'data\\transcripts_data\\'
    else:
        path = 'data\\video_data\\'
    # if user:
    user_channel_name = input("Enter your youtube channel name : ")
    # if non_user:
    competitors_channel_names = input("Enter competitors channel names separated by commas : ")
    input_list = competitors_channel_names.split(',')
    competitors_channel_names = [name.strip() for name in input_list]
    return final_data(user, non_user, user_channel_name, competitors_channel_names, transcript,path)

main(False,True,True)


##### Improvements

'''
Condition for transcription needed or not for user and competitors separately  
Testing to get all the video data from youtube, currently 7-14% missing videos


'''


