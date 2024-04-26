from dotenv import load_dotenv

load_dotenv() ##load all the nevironment variables
import os
import google.generativeai as genai
import time,json
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import pandas as pd
# from youtube_api import YoutubeDataApi



genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are Professional Yotube video summarizer. Create a concise and comprehensive summary of the provided 
            video transcription text while adhering to these guidelines:

            Craft a summary that is detailed, thorough, in-depth, and complex, while maintaining clarity and conciseness.
            Incorporate main ideas and essential information, eliminating extraneous language and focusing on critical aspects
            of what the video is about.
            Rely strictly on the provided text, without including external information.
            Format the summary in paragraph form for easy understanding.
            You should also explain in about 100-150 words of what exatcly happening in this youtube video is about as third person point of view. 
            Also provide a list of the most important keywords in the text as tagged words about 10 at the most.
            Give the response in json format starting with summary ,tags and overview as keys.
                
            Here is the output JSON schema strictly stick to the same format:{"summary":"","tags":[],"overview":""}           
            Please provide the summary in under 200 words of the text given here: """


df=pd.read_csv('thearmchairhostorian_transcripts.csv',index_col=False)

df['character_count']=df['transcript'].str.len()
df['word_count']=df['transcript'].str.split().apply(len)



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
    },
]

def generate_gemini_content(transcript_text,prompt):

    model = genai.GenerativeModel("gemini-pro",safety_settings=safety_settings)
    response = model.generate_content(prompt + transcript_text)
    return response.text

transcript_lists=df['transcript'].to_list()


response_json=[]
summary_list=[]
tag_list=[]
overview=[]
summary_error_list=[]

start=time.time()
for ind,transcript in enumerate(transcript_lists):
    print(ind)
    try:
        if transcript!='No Transcript':
            response=generate_gemini_content(transcript,prompt)
            print('Content summarized')
            response=json.loads(response.replace('\n',''))
            print('Output in json format')
            summary_list.append(response['summary'])
            tag_list.append(response['tags'])
            overview.append(response['brief'])
            response_json.append(response)
        else:
            summary_list.append('None')
            tag_list.append('None')
            overview.append('None')
            response_json.append('None')

    except Exception as e:
        print(e)
        print(f'Error at video id : {df.iloc[ind,1]}')
        summary_error_list.append(df.iloc[ind,1])
        summary_list.append('None')
        tag_list.append('None')
        overview.append('None')
        response_json.append('None')
              
end=time.time()
print(f'Total time took {(end-start)/60}')


# df.to_csv('the_armchair_historian_summary.csv')