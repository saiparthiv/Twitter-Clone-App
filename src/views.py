# In this file we derive data from command arguments and other database functions and then parse them. Once it is parsed, It finally executes the given commands.

from . import users_db,followers_db,tweets_db, updates_db, groups_db
from colorama import init, Fore, Back, Style
import socket
tokenCounter = 1
#An empty dictionary to map sessionID to username.
logData = {}
toSessionID = {}

#This function executes when a client establishes connection to the server's socket.
def init(data):
    global tokenCounter
    tokenCounter += 1
    return str(tokenCounter)

#Function to check the client's login status
def login(data):
    if len(data) != 3:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    username, password,sessionID = data
    if sessionID in logData:
        return Fore.BLUE + "Already logged in!" + Fore.WHITE
    if users_db.login(username,password):
        logData[sessionID] = username
        toSessionID[username] = sessionID
        return Fore.GREEN + "Logged in Successfully!" + Fore.WHITE
    return Fore.RED + "Invalid Username/Password" + Fore.WHITE

#Function to check if a username has been already registered.
def register(data):
    if len(data) != 4:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    username, password, repassword, sessionID = data
    if sessionID in logData:
        return Fore.BLUE + "Already logged in!" + Fore.WHITE
    elif password != repassword:
        return Fore.RED + "Password doesn't match" + Fore.WHITE
    elif users_db.register(username, password):
        logData[sessionID] = username
        toSessionID[username] = sessionID
        return Fore.GREEN + "Welcome to Twitter App, " + Fore.BLUE + username + Fore.WHITE + " !!!" + Fore.WHITE
    else:
        return Fore.RED + "User already exists" + Fore.WHITE

#Function to logout.
def logout(data):
    if len(data) != 1:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    sessionID = data[0]
    if sessionID not in logData:
        return Fore.RED + "Need to be logged in first." + Fore.WHITE
    else:
        if users_db.logout(logData[sessionID]):
            toSessionID.pop(logData[sessionID])
            logData.pop(sessionID)
            return Fore.GREEN + "$Logged_out$" + Fore.WHITE
        else:
            return Fore.RED + "Cannot logout" + Fore.WHITE

#Function to add a certain user to the list of followers.
def add_follower(data):
    if len(data) != 2:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    followed, sessionID = data
    if sessionID not in logData:
        return Fore.RED + "Need to login first" + Fore.WHITE
    follower = logData[sessionID]
    return followers_db.add_follower(follower, followed)

#Function to remove a certain follower from the list of followers.
def remove_follower(data):
    if len(data) != 2:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    followed, sessionID = data
    if sessionID not in logData:
        return Fore.RED + "Need to login first" + Fore.WHITE
    follower = logData[sessionID]
    return followers_db.remove_follower(follower, followed)

#Function to retrieve a profile and view its profile stats like followers, following, tweets, etc.
def view_profile(data):
    if len(data) != 2:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    username, sessionID = data
    return users_db.view_profile(username)

#Function to search for a username from the list of users.
def search(data):
    if len(data) != 2:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    pattern, sessionID = data
    return users_db.search(pattern)

def post_tweet(data):
    if len(data) < 2:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    sessionID = data[-1]
    if sessionID not in logData:
        return Fore.RED + "Need to login first." + Fore.WHITE             
    username, body = logData[sessionID], " ".join(data[: -1])
    return tweets_db.post_tweet(username,body)

#Function to retrieve the most trending hashtags.
def fetch_trending(data):
    return tweets_db.fetch_trending()

#Function to send private message to another user.
def send_msg(data):
    if len(data) < 3:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    if data[-1] not in logData:
        return Fore.RED + "Need to login first" + Fore.WHITE
    sendto, message, sessionID = data[0], " ".join(data[1:-1]) ,data[-1]
    is_follower = followers_db.is_follower(logData[sessionID], sendto)
    if not is_follower:
        return Fore.RED + "Can only chat with followers" + Fore.WHITE
    if sendto not in toSessionID:
        return Fore.GREEN +  "the target is not online." + Fore.WHITE
    sendtoport = toSessionID[sendto]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", int(sendtoport)+1024))
    sock.send(bytes(Fore.CYAN +logData[sessionID] + Fore.WHITE + " :: {}".format(message),"utf-8"))
    sock.close()
    return Fore.GREEN + "Message sent." + Fore.WHITE

#fetch the updates for the given username
def fetch_updates(data):
    if len(data) not in [1, 3]:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    sessionID = data[-1]
    if sessionID not in logData:
        return Fore.RED + "Need to login first" + Fore.WHITE
    username = logData[sessionID]
    print(data, len(data))
    if len(data) == 3:
        if data[0]=="mark" and data[1]=="read":
            return updates_db.mark_read(username)
    return updates_db.fetch_updates(username)

#Function to broadcast messages in a created group.
def group_chat(data):
    sessionID = data[-1]
    if sessionID not in logData:
        return Fore.RED + "Need to log in first" + Fore.WHITE
    if len(data) < 3:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    username = logData[sessionID]
    groupname = data[0]
    msgBody = " ".join(data[1 : -1])
    membersList = groups_db.fetch_members(username, groupname, True)
    if not membersList:
        return Fore.RED + "You are not member of the group" + Fore.WHITE
    for targetUser in membersList:
        if targetUser not in toSessionID or targetUser == username:
            continue
        try:
            sendtoport = toSessionID[targetUser]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", int(sendtoport)+1024))
            sock.send(bytes("Group " + Fore.CYAN + groupname + Fore.WHITE + " :: " + Fore.CYAN + username + Fore.WHITE + " " + msgBody,"utf-8"))
            sock.close()
        except:
            pass

#Function to create, delete, add, remove a group with members.
def group(data):
    sessionID = data[-1]
    if len(data) < 2:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    if sessionID not in logData: # put in server
        return Fore.RED + "Need to log in first" + Fore.WHITE
    if data[0] not in ["create","add","remove","members","delete"]:
        return Fore.RED + "Invalid command" + Fore.WHITE
    username = logData[sessionID]
    groupname = data[1]
    if data[0] == "create":
        return groups_db.create_group(username,groupname)
    elif data[0] == "add":
        return groups_db.add_member(username,data[2:-1],groupname)
    elif data[0]=="remove":
        return groups_db.remove_member(username,data[2:-1],groupname)
    elif data[0]=="members":
        members =  groups_db.fetch_members(username,groupname)
        if not members:
            return Fore.RED + "Does not have access to group members list" + Fore.WHITE
        return "Members : " + " ".join(members)
    elif data[0]=="delete":
        return groups_db.remove_group(username,groupname)

#Function to generate feed for the logged in user.
def fetch_feed(data):
    sessionID, numTweets, numPage = data[-1], 5, 1
    if sessionID not in logData:
        return Fore.RED + "Need to login first" + Fore.WHITE
    username = logData[sessionID]
    if len(data) == 2:
        numTweets = int(data[0])
    elif len(data) == 3:
        numTweets, numPage = int(data[0]), int(data[1])
    elif len(data) > 3:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    tweets = tweets_db.fetch_feed(username, numTweets, numPage)
    return "".join(tweets)

#Function to fetch tweets based on a given hashtag.
def fetch_hashtag(data):
    numTweets, numPage = 5, 1
    hashtag = data[0]
    if len(data) == 3:
        numTweets = int(data[1])
    elif len(data) == 4:
        numTweets, numPage = int(data[1]), int(data[2])
    elif len(data) > 3:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    tweets = tweets_db.fetch_tweets_by_tag(hashtag, numTweets, numPage)
    return "".join(tweets)

#Function to fetch the tweets of currently logged in users.
def fetch_posts(data):
    numTweets, numPage = 5, 1
    if data[-1] not in logData:
        return "Login first to see posts"
    username = logData[data[-1]]
    if len(data) == 2:
        numTweets = int(data[0])
    elif len(data) == 3:
        numTweets, numPage = int(data[0]), int(data[1])
    elif len(data) > 3:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    tweets = tweets_db.fetch_posts(username, numTweets, numPage)
    return "".join(tweets)

#Function to pin a tweet to the profile.
def pin_tweet(data):
    if data[-1] not in logData:
        return Fore.RED + "Login first to see posts" + Fore.WHITE
    username = logData[data[-1]]
    if len(data)==2:
        tweet_id = int(data[0])
    else:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    if tweets_db.pin_tweet(username,tweet_id):
        return Fore.GREEN + "Pin Successful" + Fore.WHITE
    return Fore.BLUE + "You have already pinned the tweet" + Fore.WHITE

def retweet_id(data):
    if data[-1] not in logData:
        return Fore.RED + "Need to login first." + Fore.WHITE
    username = logData[data[-1]]
    if len(data)==2:
        tweet_id = int(data[0])
    else:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    return tweets_db.retweet_id(username,tweet_id)

#Function to fetch list of all online followers.
def fetch_online(data):
    sessionID, numFollowers, numPage = data[-1], 5, 1
    if sessionID not in logData:
        return Fore.RED + "Need to login first" + Fore.WHITE
    username = logData[sessionID]
    if len(data) == 2:
        numFollowers = int(data[0])
    elif len(data) == 3:
        numFollowers, numPage = int(data[0]), int(data[1])
    elif len(data) > 3:
        return Fore.RED + "Invalid arguments" + Fore.WHITE
    online_followers = []
    followers = followers_db.fetch_online(username)
    for member in followers:
        if member in toSessionID:
            online_followers.append(Fore.GREEN + "*" + Fore.WHITE + member)
    s,e  = ( numPage - 1) * numFollowers , numPage * numFollowers
    return ("\n").join(online_followers[s : e])
        
