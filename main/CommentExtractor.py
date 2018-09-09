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

    def _generate_dataframe(self):
        """Create dataframe from self.data (list)
        Return (pandas.Dataframe) dataframe containing comments as rows
        """
        names = ["comment-text", "like-count", "viewer-rating", "publish-time"]
        df = pd.DataFrame(self.data, columns=names)
        return df

    def _extract_comment(self, comment):
        """Extracts data from comment and append it to self.data as a list item
            :comment (youtube#comment resource): comment in api response
        """
        commentText = comment["snippet"]["textDisplay"]
        commentText = " ".join(commentText.split("\n")).replace('"', "")
        likes = comment["snippet"]["likeCount"]
        viewerRating = comment["snippet"]["viewerRating"]
        publishTime = comment["snippet"]["publishedAt"]
        # row = "\t".join(["'"+commentText+"'", str(likes), str(viewerRating), str(publishTime)])
        self.data.append([commentText, likes, viewerRating, publishTime])
        

    def _traverse_thread_list(self, comment_thread_list):
        """Traverses the thread list to extract main comment thread and it's replies
        to store it in self.data (list)
            :comment_thread_list (youtube#commentThread resource): comment thread in api response
        """
        for comment_thread in comment_thread_list["items"]:
            self._extract_comment(comment_thread["snippet"]["topLevelComment"])
            if comment_thread["snippet"]["totalReplyCount"] > 0:
                for reply in comment_thread["replies"]["comments"]:
                    self._extract_comment(reply)

    def _get_comment_threads(self, video_id, next_page_token=None):
        """Retreives comments for a given video_id
        Return (dict) response from api call
            
            :video_id (str): id of the youtube video extracted from the url link
            :next_page_token (str): token to fetch next page of comment threads
        """
        params = dict({
            "key": self.key,
            "textFormat": "plainText",
            "part": "snippet,replies",
            "pageToken": next_page_token,
            "maxResults": self.max_results,
            "videoId": video_id
        })
        url = "/".join([self.base_url, "commentThreads"])
        response = requests.get(url, params=params)

        return response.json()

    def get_video_comments(self, video_id, target_file=None):
        """Fetch comments for the video and return as a dataframe
        Return (pandas.Dataframe)
            
            :video_id (str): id of the youtube video extracted from the url link
            :TODO target_file(str): path of target file where comments should be stored 
        """
        match = self._get_comment_threads(video_id)
        if "nextPageToken" not in match:
            self._traverse_thread_list(match)
        else:
            while "nextPageToken" in match:
                self._traverse_thread_list(match)
                next_page_token = match["nextPageToken"]
                match = self._get_comment_threads(video_id, next_page_token)

        return self._generate_dataframe()
