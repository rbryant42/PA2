from socket import *
import sys
import protocol
import json
import threading


users = set()
all_tweets = dict()

def main(args):
	# Server Port from command
	serverPort = int(sys.argv[1])
	# check that server port is in correct range
	# initialize empty message
	# create socket
	serverSocket = socket(AF_INET, SOCK_STREAM)
	# serverSocket.setblocking(False)
	# bind socket to server port
	serverSocket.bind(('', serverPort))
	# wait for client to connect
	serverSocket.listen(5)
	print('The server is ready to connect...')
	inputs =[serverSocket]
	outputs = []
	# accept connection to client
	while True:
		connectionSocket, addr = serverSocket.accept()
		print("IN MAIN")
		# connectionSocket.setblocking(False)
		print("Connected to: ", addr[0])
		# Receive message from client
		usr = connectionSocket.recv(1024).decode()
		if usr in users:
			connectionSocket.send("taken".encode())
			inputs.remove(s)
		elif usr not in users:
			connectionSocket.send("valid".encode())
			users.add(usr)
			print('user added: ', usr)
			threading.Thread(target = newClient, args = (connectionSocket, addr, usr)).start()

def newClient(connectionSocket, addr, usr):
	# Receive message from client
	connected = True
	while connected:
		print("IN THREAD")
		cmd = connectionSocket.recv(1024).decode()
		print(cmd)
		if cmd == "exit":
			connected = False
			connectionSocket.close()
			users.remove(usr)
			print('removed: ', usr)
			print("Diconnected from: ", addr[0])
		elif cmd == "tweet":
			tweetbody = connectionSocket.recv(1024).decode('utf-8')
			tweetbody = json.loads(tweetbody)
			tweet = tweetbody[0]
			hashtag = tweetbody[1]
		elif cmd == "getusers":
			connectionSocket.send(users)


if __name__ == '__main__':
	main(sys.argv)