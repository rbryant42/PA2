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
# queue containing messages to be sent to a user
# {user: list of tweets to be sent}
subscriptionQueue = {}

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
		# connectionSocket.setblocking(False)
		print("Connected to: ", addr[0])
		# Receive message from client
		usr = connectionSocket.recv(1024).decode()
		if usr in users_and_tweets:
			connectionSocket.send("taken".encode())
		elif usr not in users_and_tweets:
			connectionSocket.send("valid".encode())
			users_and_tweets[usr] = list()
			subscriptionQueue[usr] = list()
			threading.Thread(target = newClient, args = (connectionSocket, addr, usr)).start()

def newClient(connectionSocket, addr, usr):
	sendThread = threading.Thread(target = servSend, args = [connectionSocket, usr])
	sendThread.setDaemon(True)
	sendThread.start()
	# Receive message from client
	subscriptionCount = 0
	connected = True
	while connected:
		print("IN THREAD" + usr)
		# empty queue of tweets that user is subscribed to

		# receive client command
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
			# receive tweet info
			tweetbody = connectionSocket.recv(1024).decode('utf-8')
			tweetbody = json.loads(tweetbody)
			# whole tweet of form: "message" #hashtag_string
			tweet = tweetbody[0]
			hashtags = tweetbody[1]
			# store users tweet
			users_and_tweets[usr].append(tweet)

			for h in hashtags:
				# if hashtag hasnt been used yet, add new entry
				if h not in hashtags_and_tweets:
					hashtags_and_tweets[h] = [tweet]
				else:
					hashtags_and_tweets[h].append(tweet)
				# add new entry in hashtags and users so users can subscribe to it
				if h not in hashtags_and_users:
					hashtags_and_users[h] = list()
				# for each user subscribed to this hashtag, append this tweet to
				# the queue of tweets to be sent to subscribers
				for u in hashtags_and_users[h]:
					msg = usr + ": " + tweet
					if msg not in subscriptionQueue[u]:
						subscriptionQueue[u].append(msg)
		elif cmd == "subscribe":
			# receive subscription
			subscription = connectionSocket.recv(1024).decode('utf-8')
			# users can subscribe to hashtag that hasn't been used in a tweet
			# so create lists in corresponding dicts
			if subscription not in hashtags_and_users:
				hashtags_and_users[subscription] = list()
				hashtags_and_tweets[subscription] = list()
			# user already subscribed to hashtag or has max subs
			if usr in hashtags_and_users[subscription] or subscriptionCount == 3:
				connectionSocket.send(SUB_OR_UNSUB_ERROR.encode())
			# user subscription request is valid
			else:
				hashtags_and_users[subscription].append(usr)
				subscriptionCount += 1
				connectionSocket.send(SUB_OR_UNSUB_SUCCESS.encode())
		elif cmd == "unsubscribe":
			unsub = connectionSocket.recv(1024).decode('utf-8')
			# #ALL unsubs the user from #ALL and any other subscriptions
			if unsub == "ALL":
				for h in hashtags_and_users:
					if usr in hashtags_and_users[h]:
						hashtags_and_users[h].remove(usr)
				subscriptionCount = 0
			# only need to remove the user and decrement the subCount if they're
			# actually subscribed to what they want to unsubscribe from
			elif unsub in hashtags_and_users.keys() and usr in hashtags_and_users[unsub]:
				hashtags_and_users[unsub].remove(usr)
				subscriptionCount -= 1
			connectionSocket.send(SUB_OR_UNSUB_SUCCESS.encode())
		elif cmd == "getusers":
			users = list(users_and_tweets.keys())
			users = json.dumps(users)
			connectionSocket.send(users.encode('utf-8'))


def servSend(connectionSocket, usr):
	while True:
		if subscriptionQueue[usr]:
			messageDump = json.dumps(subscriptionQueue[usr])
			connectionSocket.send(messageDump.encode('utf-8'))
			subscriptionQueue[usr] = list()


if __name__ == '__main__':
	main(sys.argv)