#This file contains all the functions related to users like account creation, login, logout, fetching user tweets and other profile info.

import sqlite3
from colorama import init, Fore, Back, Style #This is used to color the output of the program.
conn = sqlite3.connect('minitweet.db') #Establish connection to the database.
c = conn.cursor()
conn2 = sqlite3.connect('minitweet.db')
c2 = conn.cursor()

#Table for storing users info
c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username VARCHAR(80) NOT NULL PRIMARY KEY UNIQUE,
        password VARCHAR(80) NOT NULL, 
        followers INT DEFAULT 0,
        following INT DEFAULT 0,
        is_online BOOL DEFAULT 1
        );
""")

conn.commit()

#Function to check if username is already registered.
def register_check(username):
    try:
        given_users = c.execute("""
            SELECT * FROM users
            WHERE username = "{}"
        """.format(username))
        for user in given_users:
            return False
        return True
    except:
        return False

#Function to register a new user.    
def register(username, password):
    if not register_check(username):
        return False
    try:
        c.execute("""
            INSERT INTO users (username, password)
            VALUES ('{}', '{}');
        """.format(username,password))
        conn.commit()
        return True
    except:
        return False

#Function to check if username and password entered are valid.
def login(username,password):
    try:
        given_users = c.execute("""
        SELECT * FROM users
        WHERE username = "{}" AND password = "{}"
        """.format(username,password))
        for user in given_users:
            c.execute("""
                UPDATE users
                SET is_online = 1
                WHERE username = '{}'
            """.format(username))
            conn.commit()
            return True
        return False
    except:
        return False

#Function to logout a given user.
def logout(username):
    try:
        c.execute("""
                UPDATE users
                SET is_online = 0
                WHERE username = '{}'
            """.format(username))
        conn.commit()
        return True
    except:
        return False

#Function to parse the tweet body and return it in a formatted string. 
def parse_tweet_body(body):
    res = body.split()
    lenb = len(res)
    for i in range(lenb):
        if res[i][0] in ['#', '@']:
            res[i] = Fore.CYAN + res[i] + Fore.WHITE
    return " ".join(res)

#Function to parse the tweet data and return it in a formatted string.
def parse_tweet(tweet_id, body, created_at):
    res = Fore.CYAN + created_at + Fore.WHITE + ":: " + Fore.BLUE+ str(tweet_id) + Fore.WHITE + "\n {} \n\n".format(parse_tweet_body(body))
    return res

#Function to fetch the tweets which are pinned by the given username for his/her profile.
def fetch_pinned_tweets(username):
    tweets = []
    try:
        pinned_tweets = c.execute(
            """
                SELECT tweets.tweet_id, pins.username, tweets.body, tweets.created_at
                FROM pins
                INNER JOIN tweets on pins.tweet_id=tweets.tweet_id
                WHERE pins.username = "{u}"
                ORDER BY id DESC
                LIMIT 5
            """.format(u=username))
        for data in pinned_tweets:
            tweets.append(parse_tweet(data[0], data[2], data[3]))
        print(tweets)
        return tweets
    except:
        return tweets

#Function to fetch the profile data of the given username.        
def view_profile(username):
    try:
        given_users = c.execute("""
            SELECT * FROM users
            WHERE username = "{}"
        """.format(username))
        does_exist = False
        curr_user = None
        for user in given_users:
            does_exist = True
            curr_user = user
        if not does_exist:
            return Fore.RED + "Given username does not exists" + Fore.WHITE
        res = Fore.GREEN + username + Fore.WHITE + " :: Followers : " + Fore.BLUE + str(curr_user[2]) + Fore.WHITE + " Following : " + Fore.BLUE + str(curr_user[3]) + Fore.WHITE + "\n" 
        pinned_tweets = fetch_pinned_tweets(username)
        for tweets in pinned_tweets:
            res += tweets
        return res
    except:
        return Fore.RED + "Invalid Username" + Fore.WHITE

#Function to search for users matching the given pattern.
def search(pattern):
    try:
        given_users = c.execute("""
            SELECT username
            FROM users
            WHERE username LIKE "{}%"
            LIMIT 5
        """.format(pattern))
        res = ""
        for user in given_users:
            res += Fore.BLUE + " # "+  Fore.WHITE + user[0] + "\n"
        return Fore.BLUE + "search results : \n" + Fore.WHITE + res
    except Exception:
        return Fore.RED + "Invalid search" + Fore.WHITE
