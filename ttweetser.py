from socket import *
from protocol import *
import sys
import json
import threading
import select
import queue

#DICTIONARY DEFINITIONS: {KEYS: VALUES}
# {username: list of this user's tweets}
users_and_tweets = dict()

# {hashtag: list of users subscribed to this hashtag}
hashtags_and_users = dict()

# {hashtag: list of tweets with this hashtag}
hashtags_and_tweets = dict()

# {connection: username}
connections_and_users = {}

# {username: connection}
users_and_connections = {}

# {connection: queue of messages to be sent on that connection}
message_queues = {}

# list of connections waiting on output
outputs = []

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

	# list of connections trying to send data to server
	inputs = [serverSocket]

	# accept connection to client
	while inputs:

		readable, writable, exceptional = select.select(inputs, outputs, inputs)

		for s in readable:
			#this case is a new connection
			if s is serverSocket:
				connectionSocket, addr = s.accept()
				connectionSocket.setblocking(0)
				inputs.append(connectionSocket)
				message_queues[connectionSocket] = queue.Queue()
			#this case is an existing connection
			else:
				try:
					msg = s.recv(1024)
				except Exception:
					print("Client disconnected")
					readable.remove(s)
					inputs.remove(s)
					continue
				# TODO: Figure out exactly what's going on

				msg = msg.decode()
				#this is a nonempty msg
				if msg:
					msg = msg.split("*")
					cmd = msg[1]
					data = msg[2:]
					command(cmd, data, s, inputs)
				#empty msg connection needs to be closed
				else:
					if s in outputs:
						outputs.remove(s)
					inputs.remove(s)
					s.close()
					del message_queues[s]

		for s in writable:
			try:
				next_msg = message_queues[s].get_nowait()
			except queue.Empty:
				outputs.remove(s)
			else:
				s.send(next_msg)


# this parses all messages and adds appropriate responses
# to message_queues[connectionSocket]
def command(cmd, data, connectionSocket, inputs):
	# connection is trying to connect as 'usr'
	if cmd == "USER":
		usr = data[0]
		if usr in users_and_tweets:
			if connectionSocket in outputs:
				outputs.remove(connectionSocket)
			inputs.remove(connectionSocket)
			connectionSocket.close()
		elif usr not in users_and_tweets:
			outputs.append(connectionSocket)
			message_queues[connectionSocket].put("*USER*valid".encode())
			connections_and_users[connectionSocket] = usr
			users_and_connections[usr] = connectionSocket
			users_and_tweets[usr] = list()

	# connection is sending a tweet

	elif cmd == "TWEET":
		tweetbody = json.loads(data[0])
		print(tweetbody)
		# whole tweet of form: "message" #hashtag_string
		tweet = tweetbody[0]
		hashtags = tweetbody[1]
		# store users tweet
		usr = connections_and_users[connectionSocket]
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
				outputs.append(users_and_connections[u])
				message_queues[users_and_connections[u]].put(msg.encode())
			print("hashtags and tweets: ", hashtags_and_tweets)
			print("hashtags_and_users: ", hashtags_and_users)
			print("message_queues", message_queues)

	# connection is subscribing to a hashtag

	elif cmd == "SUB":
		subscription = data[0]
		usr = connections_and_users[connectionSocket]
		# user can subscribe to nonexitent hashtag
		if subscription not in hashtags_and_users:
			hashtags_and_users[subscription] = list()
			hashtags_and_tweets[subscription] = list()
		# user already subscribed to hashtag or has max subs
		if usr in hashtags_and_users[subscription]:
			outputs.append(connectionSocket)
			message_queues[connectionSocket].put(SUB_OR_UNSUB_ERROR.encode())

		# user subscription request is valid
		else:
			hashtags_and_users[subscription].append(usr)
			print(hashtags_and_users)
			#subscriptionCount += 1
			outputs.append(connectionSocket)
			message_queues[connectionSocket].put(SUB_OR_UNSUB_SUCCESS.encode())
			print(message_queues)

	# connection is unsubscribing from a hashtag

	elif cmd == "UNSUB":
		unsub = data[0]
		usr = connections_and_users[connectionSocket]
		# #ALL unsubs the user from #ALL and any other subscriptions
		if unsub == "ALL":
			for h in hashtags_and_users:
				if usr in hashtags_and_users[h]:
					hashtags_and_users[h].remove(usr)
			#subscriptionCount = 0
		# only need to remove the user and decrement the subCount if they're
		# actually subscribed to what they want to unsubscribe from
		elif unsub in hashtags_and_users.keys() and usr in hashtags_and_users[unsub]:
			hashtags_and_users[unsub].remove(usr)
			#subscriptionCount -= 1
			print(hashtags_and_users)
		outputs.append(connectionSocket)
		message_queues[connectionSocket].put(SUB_OR_UNSUB_SUCCESS.encode())

	# connection wants to exit
	##THIS NEEDS TO BE FIXED##

	if cmd == "exit":
		connectionSocket.close()
		users_and_tweets.pop(usr)
		users_and_hashtags.pop(usr)
		print('removed: ', usr)
		print("Diconnected from: ", addr[0])

	if cmd == "adminserverclose":
		print("Closing server...")
		exit()

	# elif cmd == "getusers":
	# 	users = list(users_and_tweets.keys())
	# 	users = json.dumps(users)
	# 	connectionSocket.send(users.encode('utf-8'))



# def newClient(connectionSocket, addr, usr):
# 	sendThread = threading.Thread(target = servSend, args = [connectionSocket, usr])
# 	sendThread.setDaemon(True)
# 	sendThread.start()
# 	# Receive message from client
# 	subscriptionCount = 0
# 	connected = True
# 	while connected:
# 		print("IN THREAD" + usr)
# 		# empty queue of tweets that user is subscribed to

# 		# receive client command
# 		cmd = connectionSocket.recv(1024).decode()
# 		print(cmd)
# 		elif cmd == "tweet":
# 			# receive tweet info
# 			tweetbody = connectionSocket.recv(1024).decode('utf-8')
# 			tweetbody = json.loads(tweetbody)
# 			# whole tweet of form: "message" #hashtag_string
# 			tweet = tweetbody[0]
# 			hashtags = tweetbody[1]
# 			# store users tweet
# 			users_and_tweets[usr].append(tweet)

# 			for h in hashtags:
# 				# if hashtag hasnt been used yet, add new entry
# 				if h not in hashtags_and_tweets:
# 					hashtags_and_tweets[h] = [tweet]
# 				else:
# 					hashtags_and_tweets[h].append(tweet)
# 				# add new entry in hashtags and users so users can subscribe to it
# 				if h not in hashtags_and_users:
# 					hashtags_and_users[h] = list()
# 				# for each user subscribed to this hashtag, append this tweet to
# 				# the queue of tweets to be sent to subscribers
# 				for u in hashtags_and_users[h]:
# 					msg = usr + ": " + tweet
# 					if msg not in subscriptionQueue[u]:
# 						subscriptionQueue[u].append(msg)
# 		elif cmd == "subscribe":
# 			# receive subscription
# 			subscription = connectionSocket.recv(1024).decode('utf-8')
# 			# users can subscribe to hashtag that hasn't been used in a tweet
# 			# so create lists in corresponding dicts
# 			if subscription not in hashtags_and_users:
# 				hashtags_and_users[subscription] = list()
# 				hashtags_and_tweets[subscription] = list()
# 			# user already subscribed to hashtag or has max subs
# 			if usr in hashtags_and_users[subscription] or subscriptionCount == 3:
# 				connectionSocket.send(SUB_OR_UNSUB_ERROR.encode())
# 			# user subscription request is valid
# 			else:
# 				hashtags_and_users[subscription].append(usr)
# 				subscriptionCount += 1
# 				connectionSocket.send(SUB_OR_UNSUB_SUCCESS.encode())
# 		elif cmd == "unsubscribe":
# 			unsub = connectionSocket.recv(1024).decode('utf-8')
# 			# #ALL unsubs the user from #ALL and any other subscriptions
# 			if unsub == "ALL":
# 				for h in hashtags_and_users:
# 					if usr in hashtags_and_users[h]:
# 						hashtags_and_users[h].remove(usr)
# 				subscriptionCount = 0
# 			# only need to remove the user and decrement the subCount if they're
# 			# actually subscribed to what they want to unsubscribe from
# 			elif unsub in hashtags_and_users.keys() and usr in hashtags_and_users[unsub]:
# 				hashtags_and_users[unsub].remove(usr)
# 				subscriptionCount -= 1
# 			connectionSocket.send(SUB_OR_UNSUB_SUCCESS.encode())
# 		elif cmd == "getusers":
# 			users = list(users_and_tweets.keys())
# 			users = json.dumps(users)
# 			connectionSocket.send(users.encode('utf-8'))


if __name__ == '__main__':
	main(sys.argv)