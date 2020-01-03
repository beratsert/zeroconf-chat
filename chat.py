import socket
import os
from _thread import *
import threading
import time
import sys

#CONFIGS
PORT=5000
messages = {}
HOST=''
USERNAME=''


def clear():

    os.system('clear')

#GETS USERNAME
def get_username():

    clear()
    global USERNAME
    print("Welcome to Python Chat!\n\n")
    USERNAME = input("To continue, please type your username..\n")
    return USERNAME

#LEARNS USER'S IP AND CALLS LISTEN THREAD
def get_ip(USERNAME):

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        global HOST
        s.connect(('10.255.255.255', 1))
        HOST = s.getsockname()[0]
    except:
        HOST = '127.0.0.1'
    finally:
        clear()
        print("Your USERNAME : %s\n" % (USERNAME))
        print("Your IP : %s\n" % (HOST))
        s.close()
        Listener_Thread()


#STARTS THREAD FOR LISTENING PACKETS
def Listener_Thread():
    listener_UDP_thread = threading.Thread(target=listener_UDP)
    listener_UDP_thread.setDaemon(True)
    listener_UDP_thread.start()
    listener_thread = threading.Thread(target=listener)
    listener_thread.setDaemon(True)
    listener_thread.start()
    enter_command()

def enter_command():
    input("\nPress Enter to continue...")
    main_menu()

#SENDS ANNOUNCE PACKETS VIA OPENING A UDP SOCKET AND BROADCASTING ANNOUNCEMENT.
def Announce():

    global PORT
    global USERNAME
    global HOST

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.settimeout(0.2)
    server.bind(("", 5000))

    packet="["+USERNAME+ ", " + HOST +", announce]"
    while True:

        server.sendto(packet.encode('ascii', 'replace'), ('<broadcast>', 5566))
        time.sleep(10)

#SHOWS MESSAGES AND POSSIBLES TO SEND MESSAGE
def show_messages():
    global messages
    clear()
    for k, v in messages.items():
        if v != None :
            print(str(k.split(',')[0]) + ": " + str(v))
    tmp2=input("Please write your message..\nType 0 to Main Menu\n")
    if tmp2=='0':
        main_menu()
    packet="["+USERNAME+ ", " + HOST +", message, "+ tmp2 +"]"
    target_ip = ""
    for k, v in messages.items():
        key = str(k.split(',')[0])
        if key != USERNAME :
            target_ip = str(k.split(',')[1]).strip()
    start_new_thread(send_packet, (target_ip, PORT, packet))
    message_log(USERNAME, HOST, tmp2)
    show_messages()

#POSSIBLES TO NAVIGATE IN MAIN MENU
def Navigator():
    tmp=input("Please type your selection..")
    if tmp == '1':
        clear()
        print("You are sending announce messages..")
        Announce_thread = threading.Thread(target=Announce)
        Announce_thread.setDaemon(True)
        Announce_thread.start()
        enter_command()
    elif tmp == '2':
        show_messages()
    else:
        clear()
        print("See you again!!")
        sys.exit(0)

#MAIN MENU FUNCTION
def main_menu():
    clear()
    print("You are in the main menu!")
    print("You are automatically responding announce messages!\n")
    print("If you want to send announce messages, please type 1")
    print("You can access your messages by typing 2\n")
    print("You can exit by typing 0")
    Navigator()

#MAIN FUNCTION
def main():
    USERNAME = get_username()
    get_ip(USERNAME)

#TAKES HOST, PORTS AND PACKET INFO AND BY OPENING PORT SENDS MESSAGES
def send_packet(host, port, packet):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((host, port))
            s.send(packet.encode('ascii', 'replace'))
            s.close()
    except:
        pass
#FORMS MESSAGE LOGS
def message_log(name,ip,message=None):

    global messages
    if not bool(message):
        if ('%s, %s' %(name,ip)) not in messages:
            messages['%s, %s' %(name,ip)] = None
    else :
        if ('%s, %s' %(name,ip)) not in messages:
            messages['%s, %s' %(name,ip)] = [message]
        elif not bool(messages['%s, %s' %(name,ip)]) :
            messages['%s, %s' %(name,ip)] = [message]
        else:
            messages['%s, %s' %(name,ip)].append("%s" %(message))

#PARSER FOR INCOMING PACKETS AND STARTS NEW THREAD FOR RESPONSE MESSAGES
def parser(data):

    if len(data) > 5 :
        packet=[]
        data=data.strip()
        data=data[1:-1]
        data=data.decode('ascii','replace')
        target_name, target_ip, target_type, *etc = data.split(',',4)
        if target_type.strip() == 'announce' :
            packet="["+USERNAME+ ", " + HOST +", response]"
            message_log(target_name.strip(), target_ip.strip())
            start_new_thread(send_packet, (target_ip.strip(), PORT, packet))
        elif target_type.strip() == 'message' :
            message_log(target_name.strip(), target_ip.strip(), str(*etc).strip())
        else :
            message_log(target_name.strip(), target_ip.strip())
def listener_UDP():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 5566))
    while True:
        data, addr = client.recvfrom(2048)
        parser(data)

#OPEN LISTEN SOCKET AND SENDS PACKETS TO THE PARSER
def listener():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST,PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            data = conn.recv(2048)
            if not data:
                break
            parser(data)
            conn.send(data)


main()
