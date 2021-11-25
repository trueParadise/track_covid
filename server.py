from socket import *
import threading
import time
import random
import re
import sys
import json


class user:
    username = None
    password_attempt = 0
    tempID = None
    lock = threading.Lock()
    min_ID = 10000000000000000000
    max_ID = 99999999999999999999
    tempIDs_valid_time = 15*60

    def __init__(self, client):
        self.client = client

    def update_tempID(self, temp_id_list):
        while True:
            if temp_id_list[self.username] < time.time():  # {"+61410999999":1596679187.404041}
                # temp id expiry, remove old record and put a new temp id in along with it's expiry time
                tempID = str(random.randint(self.min_ID, self.max_ID))
                self.tempID = tempID
                un = self.username
                start_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(time.time()))
                expiry_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(time.time() + self.tempIDs_valid_time))
                record = un + " " + tempID + " " + start_time + " " + expiry_time
                # send new tempID to client
                self.client.send(tempID.encode())

                tempID_expiry_time = time.time() + self.tempIDs_valid_time
                self.lock.acquire()
                temp_id_list.pop(self.username)
                temp_id_list[self.username] = tempID_expiry_time
                f = open("tempIDs.txt", 'a')
                f.write(record + "\n")
                f.close()
                self.lock.release()


class Server:
    # information about login(users)----------
    user_keywords = {}
    account_state = {}
    block_list = {}
    # information about tempID-----------
    tempIDs = {}
    # -----------------------------------
    client_pool = []
    maximum_temp = 3
    min_ID = 10000000000000000000
    max_ID = 99999999999999999999
    lock = threading.Lock()
    tempIDs_valid_time = 15*60
    user_contact_list = []

    def __init__(self, server_port, block_duration):
        try:
            self.serverSocket = socket(AF_INET, SOCK_STREAM)
            self.serverSocket.bind(("127.0.0.1", server_port))
            self.serverSocket.listen(10)
            self.block_duration = block_duration
        except:
            print("fail to assign port.")
            exit()

        # read credentials information
        with open("credentials.txt", 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip().split(" ")
                self.user_keywords[line[0]] = line[1]
                self.account_state[line[0]] = "logout"

    def generate_tempID(self, user):
        tempID = str(random.randint(self.min_ID, self.max_ID))
        user.tempID = tempID
        un = user.username
        start_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(time.time()))
        expiry_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(time.time() + self.tempIDs_valid_time))
        record = un + " " + tempID + " " + start_time + " " + expiry_time
        tempID_expiry_time = time.time() + self.tempIDs_valid_time
        # put record's expiry time(float) in to tempIDs{}
        self.tempIDs[un] = tempID_expiry_time
        f = open("tempIDs.txt", 'a')
        self.lock.acquire()
        f.write(record + "\n")
        self.lock.release()
        f.close()
        return tempID

    def timer(self, username, block_list):
        self.lock.acquire()
        block_list.pop(username)
        self.lock.release()

    def authentication(self, user, username, password):
        msg = ""
        if user.password_attempt == self.maximum_temp:
            # print("----------")
            msg += "be blocked:" + str(self.block_duration)
            # add to block list, until block duration past.
            self.block_list[username] = "block"
            timer = threading.Timer(self.block_duration, self.timer, (username, self.block_list,))
            timer.start()
            user.password_attempt = 0
        elif username not in self.user_keywords:
            # print("0")
            msg += "wrong:0"
        else:
            if password != self.user_keywords[username]:
                # print("1")
                msg += "wrong:1"
                user.password_attempt += 1
            elif password == self.user_keywords[username] and self.account_state[username] == "logout" \
                    and username not in self.block_list:
                # print("2")
                # msg += "correct"
                user.password_attempt = 0
                self.account_state[username] = "login"
                user.username = username
                # when login, immediately assign a tempID to this user. And store tempID into tempIDs.txt
                # And send tempID to client
                tempID = self.generate_tempID(user)
                msg += "correct" + " " + tempID

                # this thread for checking if tempID is expired. If expiry, generate new one and send it to client.
                checking_expiry = threading.Thread(target=user.update_tempID, args=(self.tempIDs,), daemon=True)
                checking_expiry.start()
            elif password == self.user_keywords[username] and self.account_state[username] == "logout" \
                    and username in self.block_list:
                msg += "be blocked"
            elif password == self.user_keywords[username] and self.account_state[username] == "login":
                # print("3")
                msg += "have logged"
        return msg

    def user_information(self):
        pass

    # handle message
    def recvfromClients(self):
        # loop client pool, if receive message, then reply it.
        while True:
            flag = 0
            for urs in self.client_pool:
                try:
                    recv = urs.client.recv(1024).decode()
                except Exception:
                    continue
                if not recv:
                    continue
                else:  # process command from clients.
                    # process log in.
                    if re.match(r'login:(\+\w+):(\w+)', recv):
                        msg = re.match(r'login:(\+\w+):(\w+)', recv)
                        ret_msg = self.authentication(urs, msg.group(1), msg.group(2))

                    else:
                        ret_msg = "wrong"
                    if recv == "Download_tempID":
                        print("\nuser:" + str(urs.username) + "\n" + "TempID:" + str(urs.tempID))
                        ret_msg = urs.tempID
                    elif recv.startswith("["):
                        self.user_contact_list = json.loads(recv)
                        print("\nreceive contact log from " + urs.username)
                        for record in self.user_contact_list:
                            print(record)

                        print("Contact log checking")
                        tempid_phone = {}
                        with open("tempIDs.txt") as fp:
                            lines = fp.readlines()
                            for line in lines:
                                ls = line.strip().split(" ")
                                tempid_phone[ls[1]] = ls[0]

                        for tempId in self.user_contact_list:
                            match = re.match(r'(\w+) (\d+/\d+/\d+ \d+:\d+:\d+) (\d+/\d+/\d+ \d+:\d+:\d+)', tempId)
                            temp_id = match.group(1)
                            print(tempid_phone[temp_id])
                            contact_time = match.group(2)
                            print(contact_time)
                            print(temp_id)

                    elif recv == "logout":
                        # remove user from client pool and delete it. And close the socket
                        urs.password_attempt = 0
                        self.account_state[urs.username] = "logout"
                        print("\n" + urs.username + " " + "logout")
                        flag = 1
                        self.client_pool.remove(urs)
                        urs.client.close()
                        del urs
                if flag == 0:
                    urs.client.send(ret_msg.encode())
                else:
                    pass

    # listening from clients
    def start(self):
        t = threading.Thread(target=self.recvfromClients, daemon=True)
        t.start()
        while True:
            client, addr = self.serverSocket.accept()
            client.setblocking(False)
            # add socket connection to the client pool
            self.client_pool.append(user(client))


if __name__ == '__main__':
    server_port = int(sys.argv[1])
    block_duration = int(sys.argv[2])
    server = Server(server_port, block_duration)
    server.start()

    # python server.py 12000 10
