import requests
import os


key = os.environ["YOUTUBE_API_KEY"]
base_url = "https://www.googleapis.com/youtube/v3"
max_results = 100


def get_comment_threads(video_id, next_page_token=None):
    """Retreives comments for a given video_id"""
    params = dict({
        "key": key,
        "textFormat": "plainText",
        "part": "snippet,replies",
        "pageToken": next_page_token,
        "maxResults": max_results,
        "videoId": video_id
    })
    url = "/".join([base_url,"commentThreads"])
    response = requests.get(url, params=params)
    return response.json()


def extract_comment(comment):
    """Extracts data from comment"""
    commentText = comment["snippet"]["textDisplay"]
    commentText = " ".join(commentText.split("\n")).replace('"',"")
    likes = comment["snippet"]["likeCount"]
    viewerRating = comment["snippet"]["viewerRating"]
    publishTime = comment["snippet"]["publishedAt"]
    row = "\t".join(["'"+commentText+"'", str(likes), str(viewerRating), str(publishTime)])
    print(row)


def traverse_thread_list(comment_thread_list):
    """Traverses the thread list to extract main comment thread and it"s replies"""
    for comment_thread in comment_thread_list["items"]:
        extract_comment(comment_thread["snippet"]["topLevelComment"])
        if comment_thread["snippet"]["totalReplyCount"] > 0:
            for reply in comment_thread["replies"]["comments"]:
                extract_comment(reply)
        

def get_video_comments(video_id):
    match = get_comment_threads(video_id)
    if "nextPageToken" not in match:
        traverse_thread_list(match)
    else:
        while "nextPageToken" in match:
            traverse_thread_list(match)
            next_page_token = match["nextPageToken"]
            match = get_comment_threads(video_id, next_page_token)
