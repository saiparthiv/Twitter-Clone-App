#This file contains all the functions related to updates like posting updates, fetching updates and other updates info.
import sqlite3
from colorama import init, Fore, Back, Style
conn = sqlite3.connect('minitweet.db')
c = conn.cursor()

#This updates the table

c.execute("""
    CREATE TABLE IF NOT EXISTS updates (
        update_id INTEGER PRIMARY KEY,
        username VARCHAR(80) NOT NULL,
        body VARCHAR(300) NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        is_read BOOL DEFAULT 0
        );
""")

conn.commit()

#This fetches the unread notifications from the database.
def fetch_updates(username):
    try:
        updates = c.execute("""
                SELECT *
                FROM updates
                WHERE is_read = 0 AND username = '{}'
                ORDER BY created_at DESC
            """.format(username))
        body = ""
        up_num = 1
        for update in updates:
            body += Fore.CYAN + "#" + str(up_num) + Fore.WHITE + " :" + update[2] + "\n"
        if not body:
            return "No Updates.\n"
        return body
    except:
        return "Unable to fetch updates"

#This marks the unread notifications as read.
def mark_read(username):
    try:
        c.execute("""
            UPDATE updates
            SET is_read = 1
            WHERE username = '{}' AND is_read = 0
        """.format(username))
        conn.commit()
        return Fore.GREEN +  "All updates marked as read." + Fore.WHITE
    except:
        return Fore.RED + "Unable to mark as read" + Fore.WHITE
