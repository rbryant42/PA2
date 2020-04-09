from socket import *
from protocol import *
import sys
import json
import select
import queue

#DICTIONARY DEFINITIONS: {KEYS: VALUES}
# {username: list of this user's tweets}
users_and_tweets = dict()

# {hashtag: list of users subscribed to this hashtag}
hashtags_and_users = dict()

# {hashtag: list of tweets with this hashtag}
hashtags_and_tweets = dict()

# {connection: (username, subscribtion_count)}
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
				msg = s.recv(1024).decode()
				#this is a nonempty msg
				if msg:
					cmd = msg[0]
					data = msg[1:]
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

	if cmd == "6":
		usr = data
		if usr in users_and_tweets:
			if connectionSocket in outputs:
				outputs.remove(connectionSocket)
			inputs.remove(connectionSocket)
			connectionSocket.close()
		elif usr not in users_and_tweets:
			outputs.append(connectionSocket)
			message_queues[connectionSocket].put("*USER*valid".encode())
			connections_and_users[connectionSocket] = [usr, 0]
			users_and_connections[usr] = connectionSocket
			users_and_tweets[usr] = list()

	# connection is sending a tweet

	elif cmd == "0":
		tweetbody = json.loads(data)
		print(tweetbody)
		# whole tweet of form: "message" #hashtag_string
		tweet = tweetbody[0]
		hashtags = tweetbody[1]
		# store users tweet
		usr = connections_and_users[connectionSocket][0]
		users_and_tweets[usr].append(tweet)

		# everyone subscribed to #ALL will receive this tweet
		subscribers = hashtags_and_users['ALL']

		# add to subscribers everyone that's subscribed to a hashtag
		# included in this tweet
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
				if u not in subscribers:
					subscribers.append(u)

		for u in subscribers:
			msg = "0" + usr + ": " + tweet
			outputs.append(users_and_connections[u])
			message_queues[users_and_connections[u]].put(msg.encode())

	# subscribe: connection is subscribing to a hashtag

	elif cmd == "1":
		subscription = data
		usr = connections_and_users[connectionSocket][0]
		sub_count = connections_and_users[connectionSocket][1]
		# user can subscribe to nonexitent hashtag
		if subscription not in hashtags_and_users:
			hashtags_and_users[subscription] = list()
			hashtags_and_tweets[subscription] = list()
		# user already subscribed to hashtag or has max subs
		if usr in hashtags_and_users[subscription] or sub_count >= 3:
			outputs.append(connectionSocket)
			message_queues[connectionSocket].put(("1" + (MAX_HASHTAGS % subscription)).encode())

		# user subscription request is valid
		else:
			hashtags_and_users[subscription].append(usr)
			sub_count += 1
			connections_and_users[connectionSocket][1] = sub_count
			outputs.append(connectionSocket)
			message_queues[connectionSocket].put(("1" + SUB_OR_UNSUB_SUCCESS).encode())

	# unsubscribe: connection is unsubscribing from a hashtag

	elif cmd == "2":
		unsub = data
		usr = connections_and_users[connectionSocket][0]
		# #ALL unsubs the user from #ALL and any other subscriptions
		if unsub == "ALL":
			print(hashtags_and_users)
			for h in hashtags_and_users:
				if usr in hashtags_and_users[h]:
					hashtags_and_users[h].remove(usr)
			connections_and_users[connectionSocket][1] = 0
			print(hashtags_and_users)
		# only need to remove the user and decrement the subCount if they're
		# actually subscribed to what they want to unsubscribe from
		elif unsub in hashtags_and_users.keys() and usr in hashtags_and_users[unsub]:
			hashtags_and_users[unsub].remove(usr)
			connections_and_users[connectionSocket][1] -= 1
		outputs.append(connectionSocket)
		message_queues[connectionSocket].put(("2" + SUB_OR_UNSUB_SUCCESS).encode())

	# getusers: connection wants list of active users

	elif cmd == "3":
		users = list(users_and_connections.keys())
		users = json.dumps(users)
		msg = ("3" + users).encode()
		outputs.append(connectionSocket)
		message_queues[connectionSocket].put(msg)

	# gettweets: connection wants all tweets from a user

	elif cmd == "4":
		user = data
		if user not in users_and_tweets:
			outputs.append(connectionSocket)
			message_queues[connectionSocket].put(("7" + "no users " + user + " in the system").encode())
		else:
			tweets = []
			for t in users_and_tweets[user]:
				tweets.append((user + ": " + t))
			tweets = json.dumps(tweets)
			outputs.append(connectionSocket)
			message_queues[connectionSocket].put(("4" + tweets).encode())



	# connection wants to exit

	elif cmd == "5":
		# remove socket from all data structures
		if connectionSocket in outputs:
			outputs.remove(connectionSocket)
		inputs.remove(connectionSocket)
		del message_queues[connectionSocket]
		# remove user from all data structures
		usr = connections_and_users[connectionSocket][0]
		del users_and_connections[usr]
		del connections_and_users[connectionSocket]
		del users_and_tweets[usr]
		for h in hashtags_and_users:
			if usr in hashtags_and_users[h]:
				hashtags_and_users[h].remove(usr)

		# end connection
		connectionSocket.close()


if __name__ == '__main__':
	main(sys.argv)