from socket import *
from protocol import *
import sys
import json
import threading

#DICTIONARY DEFINITIONS: {KEYS: VALUES}
# {username: list of this user's tweets}
users_and_tweets = dict()
# {hashtag: list of users subscribed to this hashtag}
hashtags_and_users = dict()
# {hashtag: list of tweets with this hashtag}
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
			print('user added: ', usr)
			threading.Thread(target = newClient, args = (connectionSocket, addr, usr)).start()

def newClient(connectionSocket, addr, usr):
	# Receive message from client
	subscriptionCount = 0
	connected = True
	while connected:
		print(users_and_tweets)
		print(hashtags_and_users)
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
				if h not in hashtags_and_users:
					hashtags_and_users[h] = list()
		elif cmd == "subscribe":
			subscription = connectionSocket.recv(1024).decode('utf-8')
			# users can subscribe to hashtag that hasn't been used in a tweet
			# so create lists in corresponding dicts
			if subscription not in hashtags_and_users:
				hashtags_and_users[subscription] = list()
				hashtags_and_tweets[subscription] = list()
			# user already subscribed to hashtag or has max subs
			if usr in hashtags_and_users[subscription] or subscriptionCount == 3:
				connectionSocket.send(SUBSCRIBE_ERROR.encode())
			# user subscription request is valid
			else:
				hashtags_and_users[subscription].append(usr)
				subscriptionCount += 1
				connectionSocket.send(SUBSCRIBE_SUCCESS.encode())
		elif cmd == "getusers":
			users = list(users_and_tweets.keys())
			users = json.dumps(users)
			connectionSocket.send(users.encode('utf-8'))


if __name__ == '__main__':
	main(sys.argv)