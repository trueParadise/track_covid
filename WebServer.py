from socket import *
import sys
import io

serverPort = int(sys.argv[1])
host = '127.0.0.1'
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((host, serverPort))
serverSocket.listen(1)
print("Sir, i am listening :")
print("Ok, now you can play with me...")
while True:
    try:
        connection, addr = serverSocket.accept()
        print("Connection from: "+ str(addr))
        my_reader = connection.recv(1024).decode()
        file = io.StringIO(my_reader)
        header = file.readline()
        first_line = header.replace("/", " ").split()
        method = first_line[0]
        file_name = first_line[1].split(".")[0]
        file_type = first_line[1].split(".")[1]
        file = file_name+"."+file_type
        # turn the file in same directory into binary file
        # and prepare for HTTP response
        if file_type == "html":
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
            # response = "HTTP/1.1 200 OK"
        elif file_type == "png":
            response = "HTTP/1.1 200 OK\r\nContent-Type: image/png\r\n\r\n"
        else:
            response = ""
        File = open(file, 'rb')
        content = File.read()
        connection.sendall(response.encode())
        connection.sendall(content)
        connection.close()
    except Exception:
        response = "HTTP/1.1 404 File not found\r\n\r\n"
        content = "<h1><center>404 Error File not found</center></h1>"
        connection.sendall(response.encode())
        connection.sendall(content.encode())
        connection.close()















