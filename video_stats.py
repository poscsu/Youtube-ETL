import requests
import json

import os
from dotenv import load_dotenv


load_dotenv(dotenv_path="./.env") 

YOUR_API_KEY = os.getenv("API_KEY")
CHANNEL = "chrisfix"
maxResults = 50


def get_channel_playlistid():

    try:

        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL}&key={YOUR_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        #print(json.dumps(data, indent=2))

        channel_item= data["items"][0]

        channel_playlistid= channel_item["contentDetails"]["relatedPlaylists"]["uploads"]
       
       # print(channel_playlistid)

        return channel_playlistid

    except requests.exceptions.RequestException as e:
        raise e



playlist_id= get_channel_playlistid()
def get_video_id(playlist_id):
    
    video_ids=[]
    pageToken= None
    base_url =  f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails%20&maxResults={maxResults}&playlistId={playlist_id}&key={YOUR_API_KEY}"
    try:
        while True:
            video_api_url= base_url
            if pageToken:
                video_api_url += f"&pageToken={pageToken}"

            response = requests.get(video_api_url)
            response.raise_for_status()
            data = response.json()
            #print(json.dumps(data, indent=2))

            for item in data.get("items",[]):
                video_id = item["contentDetails"]["videoId"]
                video_ids.append(video_id)
                
            pageToken=data.get("nextPageToken")
            if not pageToken:
                break

        # print(video_ids)
        return video_ids


    except requests.exceptions.RequestException as e:
        raise e



video_ids = get_video_id(playlist_id)

def get_video_stats(video_ids):
    video_stats=[]
    def batch_list(video_idlst,batch_size):
        """Yield successive n-sized chunks from lst."""
        for i in range(0,len(video_idlst), batch_size):
            yield video_idlst[i:i + batch_size]
        
    try:
        for batch in batch_list(video_ids, maxResults):
            video_ids_query= ",".join(batch)

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_query}&key={YOUR_API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data= response.json()

            for item in data.get('items',[]):
                video_id=item['id']
                snippet=item['snippet']
                contentDetails=item['contentDetails']
                statistics=item['statistics']  
            
                video_stats.append({
                        'video_id': video_id,
                        'title': snippet['title'],
                        'publishedAt': snippet['publishedAt'],
                        'duration': contentDetails['duration'],
                        'viewCount': statistics.get('viewCount',0),
                        'likeCount': statistics.get('likeCount',0),
                        'commentCount': statistics.get('commentCount',0)

                })
        return video_stats
    except requests.exceptions.RequestException as e:
        print(f"Error fetching video stats: {e}")
        raise
    
#print(get_video_stats(video_ids))
        


if __name__== "__main__":
    playlist_id=get_channel_playlistid()
    video_ids=get_video_id(playlist_id)
    video_stats=get_video_stats(video_ids)





