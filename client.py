import socket       # Imports socket library
import sys, os      
import atexit       # What this library does is it interrupts keyboard and runs at exit.
import multiprocessing  
from getpass import getpass
from colorama import init, Fore, Back, Style

manager = multiprocessing.Manager()
shared = manager.dict()

#It operates a chat-server in the background as a distinct forked process that listens for client chat messages.
def new_server_sided_chat_func():
    def server_chat(ip, port, shared):
        while 1:
            try:
                sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,True)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT,True)
                sock.bind(("localhost",port))
                sock.listen(5)
                c,addr = sock.accept()
                while 1:
                    data = c.recv(1024).decode()
                    print(data)
                    if data=="":
                        break
            except socket.timeout:
                try:
                    sock.close()
                except:
                    pass
    return server_chat

server_chat = new_server_sided_chat_func()


# Timeout for the client connection
socket.setdefaulttimeout(3)

# Create a new TCP Client.
def new_tcp_client():
    class client:
        def __init__(self,ip,port,command):
            self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
            self.sock.connect((ip,port))    
            self.sock.send(bytes(command,"utf-8"))
            data = ""
            try:
                while 1:
                    k = self.sock.recv(10000).decode() 
                    data += k
                    if not k:
                        break        
                
            except socket.timeout: 
                pass
            self.data = data
    return client

client = new_tcp_client()  

#Ensures that the user is logged out if the client encounters an exception or shuts down.
def logout_check(client):
    def logout_exit():
        client("localhost", 12345, "logout")
    return logout_exit

logout_exit = logout_check(client)

#Generates an unique sessionID for the client server
#Identifies the client and state of the server using the sessionID
sessionID = client("localhost",12345,"init").data
#Default is guest for unlogged in users
sessionUser = 'guest'
print(sessionID)

server_process = multiprocessing.Process(target=server_chat,args=("localhost",int(sessionID)+1024,shared))
server_process.start()
atexit.register(logout_exit)

def main_validation_func(client, sessionID, sessionUser):
    while True:
        command = input(Fore.YELLOW + "{} : ".format(sessionUser) + Fore.WHITE)
    #This opens the text editor 'Nano' for sending a longer tweet
        if command == "tweet":
            file = open("data/tweet{}.txt".format(sessionID),"w")
            file.close()
            os.system("nano data/tweet{}.txt".format(sessionID))
            command = input(Fore.YELLOW +  "Are you sure to post the tweet Y/N : " + Fore.WHITE)
            if command[0] == 'y' or command[0] == 'Y':
                tweet = open("data/tweet{}.txt".format(sessionID),"r")
                s = tweet.read(200)
                tweet.close()
                recData = client("localhost",12345,"tweet " + s + " " + sessionID).data
                print(recData)
            else :
                print(Fore.RED + "Tweet posting has been cancelled!" + Fore.WHITE)
            continue
    #Password is entered in asterix format for login so that it's secure
        elif command[:5] == "login":
            password = getpass(Fore.BLUE + 'Please enter your Password: ' + Fore.WHITE)
            command += " " + password
    #Password is entered in asterix format twice for register so that its revalidated for typos
        elif command[:8] == "register":
            password = getpass(Fore.BLUE + 'Please enter your Password: ' + Fore.WHITE)
            repassword = getpass(Fore.BLUE + 'Please re-enter your Password: ' + Fore.WHITE)
            command+=" "+password+" "+repassword
        
    #Every message request is tagged with sessionID
        recData = client("localhost",12345,command+" "+sessionID).data

    #This changes the sessionUser variable when a user either logsout or logins or registers
        if recData.find("$Logged_out$")!=-1 :
            sessionUser = "guest"
            print(Fore.GREEN + "Logged Out Successfully !!!" + Fore.WHITE)
            continue
        elif recData.find("Logged in ")!=-1 or recData.find("Welcome") != -1:
            sessionUser = command.split()[1]
        print(recData)

main_validation_func(client, sessionID, sessionUser)
