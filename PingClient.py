
# version python3.7

from socket import *
import sys
from datetime import datetime

ServerName = sys.argv[1]
ServerPort = int(sys.argv[2])


# create an UDP connection
clientSocket = socket(AF_INET, SOCK_DGRAM)

RTT_List = []

pack_lost = 0

for i in range(15):
	time_stamp = datetime.now().isoformat(sep=" ")[:-3]
	ping_message = "PING" + str(3331+i) + " " + time_stamp+'\r\n'
	time_send = datetime.now()
	clientSocket.sendto(ping_message.encode(),(ServerName, ServerPort))

	try:
		clientSocket.settimeout(0.6)
		clientSocket.recvfrom(1024)
		time_receive = datetime.now()
		rtt = round((time_receive-time_send).total_seconds()*1000)
		RTT_List.append(rtt)
		print(f'PING to {ServerName}, seq = {3331+i}, rtt={rtt} ms')
		clientSocket.settimeout(None)
	except timeout:
		pack_lost += 1
		print(f'PING to {ServerName}, seq = {3331+i}, timeout')



print("\n")
print(f'Minimum RTT = {min(RTT_List)} ms')
print(f'Maximum RTT = {max(RTT_List)} ms')
print(f'Average RTT = {round(float(sum(RTT_List) / len(RTT_List)))} ms')
print(f'{round(float(pack_lost) / 15 * 100)}% of packets have been lost through the network')
clientSocket.close()
