import pandas as pd
import numpy as np
# from openai import OpenAI
import openai
import tiktoken
import os
from dotenv import load_dotenv
load_dotenv()

# def num_tokens_from_string(summary_list, encoding) -> int:
#     """Returns the number of tokens in a text string."""
#     token_count=[]
#     for summary in summary_list:
#         token_count.append(len(encoding.encode(summary)))
#     return token_count


# Set up your OpenAI API key
def set_api_key():
    print('Setting OPENAI API KEY...')
    api_key = os.getenv('OPENAI_API_KEY')
    openai.api_key = api_key



# user_channel_name = 'TheArmchairHistorian'
def get_summaries(path, user_channel_name):
    user_df = pd.read_csv(f"{path}{user_channel_name}_summary.csv").dropna().reset_index(drop=True)
    competitors_df=pd.read_csv(f"{path}{user_channel_name}_competitors_summary.csv").dropna().reset_index(drop=True)
    return user_df, competitors_df

def get_embeddings(summary_list,model_name):
    embeddings_list=[]
    for summary in summary_list:
        response = openai.embeddings.create(input=summary,model=model_name).data[0].embedding
        embeddings_list.append(response)
    return embeddings_list

def save_embeddings(path,user_df,competitors_df,user_channel_name):
    user_df.to_csv(f"{path}{user_channel_name}_embeddings.csv")
    competitors_df.to_csv(f"{path}{user_channel_name}_competitors_embeddings.csv")


def calculate_cosine_similarities(user_embeddings,competitor_embeddings):
# Calculate cosine similarity between each video summary of Creator and each video summary of its competitors
    cosine_similarities = []
    for user_embedding in user_embeddings:
        similarities = [np.dot(user_embedding, comp_embedding) / (np.linalg.norm(user_embedding) * np.linalg.norm(comp_embedding)) for comp_embedding in competitor_embeddings]
        cosine_similarities.append(similarities)

def get_smallest_indices(cosine_similarities,limit):
    arr=np.array(cosine_similarities)
    flat_indices = np.argsort(arr, axis=None)[:limit]
    indices = np.unravel_index(flat_indices, arr.shape)
    return np.unique(indices[1])

def count_index(cosine_similarities,limit):
    index_count=0
    count=0
    
    while index_count<limit:
        # print(count)
        indices=get_smallest_indices(cosine_similarities,limit+count)
        # print(indices)
        index_count=len(indices)
        count+=1

    return indices

def video_recommendation(path, video_count,model_name,user_channel_name):
    user_df, competitors_df = get_summaries(path['summary_path'],user_channel_name)
    competitors_df.to_csv(f"{path['interim_path']}{user_channel_name}_comp_data.csv")

    user_summary_list=user_df['summary'].tolist()
    competitors_summary_list=competitors_df['summary'].tolist()
    # Generate embeddings for Creator A's video summaries
    print('Getting embeddings for user summaries...')
    user_embeddings=get_embeddings(user_summary_list,model_name)
    # Generate embeddings for competitors' video summaries
    print('Getting embeddings for competitors summaries...')

    competitor_embeddings=get_embeddings(competitors_summary_list,model_name)
    
    user_df['text_embeddings']=user_embeddings
    competitors_df['text_embeddings']=competitor_embeddings
    print('Calculating siimilarity scores between user and competitors videos...')
    cosine_similarities=calculate_cosine_similarities(user_embeddings,competitor_embeddings)
    print('Fetching top video ideas which user not implemented yet...')
    indices = count_index(cosine_similarities,video_count)
    results_df=competitors_df.loc[indices,:][['video_title','summary']]

    results_df.to_csv(f"{path['interim_path']}{user_channel_name}_video_recommended.csv")
    print(results_df)
    
    save_embeddings(path['embedding_path'],user_df,competitors_df,user_channel_name)

    return results_df

def main():

    summary_path = 'data\\summary_data\\'
    embedding_path = 'data\\embedding_data\\'
    model_name='text-embedding-ada-002'
    video_count = 5

    path = {
        'summary_path' :'data\\summary_data\\',
        'embedding_path' : 'data\\embedding_data\\',
        'interim_path' : 'data\\interim\\'
    }

    user_channel_name = input("Enter your youtube channel name : ")

    video_recommendation(path, video_count, model_name, user_channel_name)

    # if user:
