from CommentExtractor import CommentExtractor

vid_lsd = 'JDjTJ6lkb-8'
vid_sma = 'G25nLDc0o44'
file_lsd = "comments_lsd.txt"

comment_extractor = CommentExtractor()
comment_extractor.get_video_comments(vid_sma, file_lsd)
