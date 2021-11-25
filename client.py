from socket import *
import threading
import time
import re
import sys
import os
import json


class Client:
    tempID = None
    is_login = False
    peer_client_pool = []
    tempIDs_valid_time = 15 * 60
    contact_log = "z5027264_contactlog.txt"
    tracing_time = 3 * 60
    records = []
    lock = threading.Lock()
    upload_contactlog = []

    def __init__(self, address, client_udp_port):
        try:
            # TCP initialization(communicate with server)
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(address)
            # UDP initialization(communicate with peer client)
            self.client_udp_port = client_udp_port
            self.p2p_serverSocket = socket(AF_INET, SOCK_DGRAM)
            self.p2p_serverSocket.bind(("127.0.0.1", client_udp_port))
        except:
            print("can not connect to server.")
            exit()

    def authentication(self):
        un = input("Please input username:")
        pw = input("Please password:")
        msg = "login:" + un + ":" + pw
        self.client_socket.send(msg.encode())
        msg = self.client_socket.recv(1024).decode()
        # print(msg)
        if msg == "wrong":
            print("Wrong form, please use internationally format mobile phone number")
        elif msg == "wrong:0":
            print("User name doesn't exist.")
        elif msg == "wrong:1":
            print("Invalid Password. Please try again")
        elif re.match(r'correct (\w+)', msg):
            tempID = re.match(r'correct (\w+)', msg).group(1)
            self.tempID = tempID
            print("Welcome to the BlueTrace Simulator!")
            self.is_login = True
            # daemon thread for checking contact log and remove record that more than 3 mins
            t = threading.Thread(target=self.maintain_contactlog, daemon=True)
            t.start()
        elif msg == "have logged":
            print("You have logged in!")
        elif re.match(r'be blocked:(\w+)', msg):
            # msg = re.match(r'be blocked:(\w+)', msg)
            print("Invalid Password. Your account has been blocked. Please try again later")
            exit()
        elif msg == "be blocked":
            print("Your account is blocked due to multiple login failures. Please try again later")
            exit()

    def p2p_handler(self, p2p_msg):
        # "06/08/2020 15:18:16"
        Time = re.match(r'(\w+) (\d+/\d+/\d+ \d+:\d+:\d+) (\d+/\d+/\d+ \d+:\d+:\d+)', p2p_msg)
        start_time = Time.group(2)
        time_tuple_s = time.strptime(start_time, "%d/%m/%Y %H:%M:%S")
        start_time_float = time.mktime(time_tuple_s)
        expiry_time = Time.group(3)
        time_tuple_e = time.strptime(expiry_time, "%d/%m/%Y %H:%M:%S")
        expiry_time_float = time.mktime(time_tuple_e)
        current_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(time.time()))
        current_time_float = time.time()
        print("Current time is: ", current_time)
        if start_time_float <= current_time_float <= expiry_time_float:
            print("The beacon is valid.")
            self.lock.acquire()
            # write in new beacon information
            f = open(self.contact_log, 'a')
            f.write(p2p_msg + "\n")
            f.close()
            self.lock.release()
        else:
            print("The beacon is invalid.")

    def maintain_contactlog(self):
        while True:
            if os.path.isfile(self.contact_log):
                time.sleep(5)
                size = os.path.getsize(self.contact_log)
                # print(size)
                if size == 0:
                    continue
                else:
                    lines = [line for line in open(self.contact_log, 'r')
                             if time.mktime(time.strptime(
                            re.match(r'(\w+) (\d+/\d+/\d+ \d+:\d+:\d+) (\d+/\d+/\d+ \d+:\d+:\d+)', line).group(2),
                            "%d/%m/%Y %H:%M:%S"))
                             + self.tracing_time > time.time()]
                    # print(lines)
                    self.lock.acquire()
                    f = open(self.contact_log, "w")
                    f.writelines(lines)
                    f.close()
                    self.lock.release()

    def listenfromCilent(self):
        while True:
            p2p_msg, p2p_addr = self.p2p_serverSocket.recvfrom(1024)
            p2p_msg = p2p_msg.decode()
            print("\nreceived beacon:\n" + p2p_msg)
            self.p2p_handler(p2p_msg)

    def beacon_send(self, addr):
        tempID = self.tempID
        start_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(time.time()))
        expiry_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(time.time() + self.tempIDs_valid_time))
        record = tempID + " " + start_time + " " + expiry_time
        print("\n" + record)
        self.p2p_serverSocket.sendto(record.encode(), addr)

    def listenfromServer(self):
        # when new tempID generate, the server will send it to client immediately
        while True:
            msg = self.client_socket.recv(1024).decode()
            # print(msg)
            self.tempID = msg

    def Upload_contactlog(self):
        with open(self.contact_log, 'r') as fp:
            lines = fp.readlines()
            for line in lines:
                print("\n" + line)
                self.upload_contactlog.append(line.strip())
        self.client_socket.send(json.dumps(self.upload_contactlog).encode())

    def logout(self, msg):
        self.client_socket.send(msg.encode())
        self.is_login = False

    def start(self):
        # new thread for listening message from clients
        client_recv_thread = threading.Thread(target=self.listenfromCilent)
        client_recv_thread.setDaemon(True)
        client_recv_thread.start()
        while True:
            while not self.is_login:
                self.authentication()

            #     new thread for listening message from server
            t = threading.Thread(target=self.listenfromServer, daemon=True)
            t.start()
            msg = input()
            if msg == "Download_tempID":
                self.client_socket.send(msg.encode())
                print("\nTempID:" + self.tempID)
            elif msg == "Upload_contact_log":
                self.Upload_contactlog()
            elif msg == "logout":
                self.logout(msg)
                exit()
            elif re.match(r"Beacon (\d+\.\d+\.\d+\.\d+) (\d+)", msg):
                match = re.match(r"Beacon (\d+\.\d+\.\d+\.\d+) (\d+)", msg)
                self.beacon_send((match.group(1), int(match.group(2))))
            else:
                print("Error. Invalid command")


if __name__ == '__main__':
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    client_udp_port = int(sys.argv[3])
    client_i = Client((server_ip, server_port), client_udp_port)
    client_i.start()

    #python client.py 127.0.0.1 12000 8000
