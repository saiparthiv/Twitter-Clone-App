# This file contains commands that user enters. We map those commands to the respective function(located in the file views.py) that we want to run. 

from . import views

functions = {
    "init":views.init,
    "login":views.login,
    "register":views.register,
    "logout":views.logout,
    "follow":views.add_follower,
    "unfollow":views.remove_follower,
    "profile":views.view_profile,
    "search":views.search,
    "tweet":views.post_tweet,
    "trending": views.fetch_trending,
    "msg": views.send_msg,
    "updates": views.fetch_updates,
    "group": views.group,
    "stream": views.group_chat,
    "feed": views.fetch_feed,
    "hashtag": views.fetch_hashtag,
    "posts": views.fetch_posts,
    "pin" : views.pin_tweet,
    "retweet" : views.retweet_id,
    "online" : views.fetch_online
}