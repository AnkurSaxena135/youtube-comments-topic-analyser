import requests
import os
import pandas as pd

import vars

class CommentExtractor():
    """Class that takes a video-id and returns it's comments as a data frame"""

    def __init__(self):
        """Initialize dataframe, video-id and target file location"""
        self.key = vars.youtube["YOUTUBE_API_KEY"]
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.max_results = 100
        self.data = []


    def get_comment_threads(self, video_id, next_page_token=None):
        """Retreives comments for a given video_id"""
        params = dict({
            "key": self.key,
            "textFormat": "plainText",
            "part": "snippet,replies",
            "pageToken": next_page_token,
            "maxResults": self.max_results,
            "videoId": video_id
        })
        url = "/".join([self.base_url,"commentThreads"])
        response = requests.get(url, params=params)
        return response.json()


    def extract_comment(self, comment):
        """Extracts data from comment"""
        commentText = comment["snippet"]["textDisplay"]
        commentText = " ".join(commentText.split("\n")).replace('"',"")
        likes = comment["snippet"]["likeCount"]
        viewerRating = comment["snippet"]["viewerRating"]
        publishTime = comment["snippet"]["publishedAt"]
        # row = "\t".join(["'"+commentText+"'", str(likes), str(viewerRating), str(publishTime)])
        self.data.append((commentText, likes, viewerRating, publishTime))
        # print(self.data)


    def traverse_thread_list(self, comment_thread_list):
        """Traverses the thread list to extract main comment thread and it"s replies"""
        for comment_thread in comment_thread_list["items"]:
            self.extract_comment(comment_thread["snippet"]["topLevelComment"])
            if comment_thread["snippet"]["totalReplyCount"] > 0:
                for reply in comment_thread["replies"]["comments"]:
                    self.extract_comment(reply)
            

    def generate_file(self, target_file):
        """Create dataframe"""
        names= ["comment-text", "like-count", "viewer-rating", "publish-time"]        
        return pd.DataFrame(self.data, columns=names)


    def get_video_comments(self, video_id, target_file=None):

        match = self.get_comment_threads(video_id)
        if "nextPageToken" not in match:
            self.traverse_thread_list(match)
        else:
            while "nextPageToken" in match:
                self.traverse_thread_list(match)
                next_page_token = match["nextPageToken"]
                match = self.get_comment_threads(next_page_token)
        
        return self.generate_file(target_file)
