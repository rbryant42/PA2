from socket import *
import sys
import protocol
import json
import threading


users_and_tweets = dict()
users_and_hashtags = dict()
hashtags_and_tweets = dict()

def main(args):
	# Server Port from command
	serverPort = int(sys.argv[1])
	# create socket
	serverSocket = socket(AF_INET, SOCK_STREAM)
	# serverSocket.setblocking(False)
	# bind socket to server port
	serverSocket.bind(('', serverPort))
	# wait for client to connect
	serverSocket.listen(5)
	print('The server is ready to connect...')
	# accept connection to client
	while True:
		connectionSocket, addr = serverSocket.accept()
		print("IN MAIN")
		# connectionSocket.setblocking(False)
		print("Connected to: ", addr[0])
		# Receive message from client
		usr = connectionSocket.recv(1024).decode()
		if usr in users_and_tweets:
			connectionSocket.send("taken".encode())
		elif usr not in users_and_tweets:
			connectionSocket.send("valid".encode())
			users_and_tweets[usr] = list()
			users_and_hashtags[usr] = list()
			print('user added: ', usr)
			threading.Thread(target = newClient, args = (connectionSocket, addr, usr)).start()

def newClient(connectionSocket, addr, usr):
	# Receive message from client
	connected = True
	while connected:
		print(users_and_tweets)
		print(users_and_hashtags)
		print(hashtags_and_tweets)
		print("IN THREAD")
		cmd = connectionSocket.recv(1024).decode()
		print(cmd)
		if cmd == "exit":
			connected = False
			connectionSocket.close()
			users_and_tweets.pop(usr)
			users_and_hashtags.pop(usr)
			print('removed: ', usr)
			print("Diconnected from: ", addr[0])
		elif cmd == "tweet":
			tweetbody = connectionSocket.recv(1024).decode('utf-8')
			tweetbody = json.loads(tweetbody)
			tweet = tweetbody[0]
			print(tweet)
			hashtags = tweetbody[1]
			print(hashtags)
			users_and_tweets[usr].append(tweet)
			for h in hashtags:
				if h not in hashtags_and_tweets:
					hashtags_and_tweets[h] = [tweet]
				else:
					hashtags_and_tweets[h].append(tweet)
		elif cmd == "getusers":
			users = list(users_and_tweets.keys())
			users = json.dumps(users)
			connectionSocket.send(users.encode('utf-8'))


if __name__ == '__main__':
	main(sys.argv)