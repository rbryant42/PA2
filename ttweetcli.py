from socket import *
import sys
from protocol import *
import json
import re
import threading
import time

###COMMANDS###
# tweet is 0, subscribe is 1, unsubscribe is 2, getusers is 3, gettweets is 4, exit is 5

socketLock = threading.Lock()
socketAvailable = threading.Condition()
timeline = []

def main(args):
	# checks number of args
	if len(args) != 4:
		# (5)
		print(WRONG_PARAMS)
		sys.exit()

	# server IP is second argument
	# (1) Maybe replace function with regex?
	serverName = args[1]
	if not validIP(serverName):
		print(INVALID_IP)
		sys.exit()

	# server port is the third argument
	serverPort = int(args[2])
	if serverPort not in range(1024, 65535+1):
		print(INVALID_PORT)
		sys.exit()

	# username is fourth argument
	username = args[3]

	# checks that username only contains alphanumeric characters
	# (3)
	if len(username) == 0 or re.search(r'[^a-zA-Z0-9]', username):
		print(INVALID_USERNAME)
		sys.exit()

	# creates client socket
	clientSocket = socket(AF_INET, SOCK_STREAM)

	# attempts to connect to server, exits if not found
	if clientSocket.connect_ex((serverName, serverPort)) != 0:
		print(INVALID_PORT)
		sys.exit()

	#check if username taken
	msg = "6" + username
	clientSocket.send(msg.encode())
	val = clientSocket.recv(1024).decode()
	if val == "*USER*valid":
		print(LOGIN_SUCCESS)
		threading.Thread(target = sendThread, args = [clientSocket]).start()
		threading.Thread(target = clientListen, args = [clientSocket], daemon = True).start()
	else:
		print(USER_ALREADY_LOGGED_IN)
		clientSocket.close()
		sys.exit()

def sendThread(clientSocket):
	def ttweet(data):
		# sent cmd
		# clientSocket.send(cmd.encode())
		### Logic comment: Not sure if we should send the command
		### before we check for input errors. Then, the server
		### may be waiting to receive something that it won't
		# handle message
		tweet = data[1]
		if tweet == None or len(tweet) == 0:
			# (7)
			print(EMPTY_MSG)
			return
		if len(tweet) > 150:
			# (6)
			print(MSG_TOO_LONG)
			return
		# put quotes back on tweet because its easier for displaying
		# the tweets in the desired format later
		tweet = prompt.split("tweet")[1].strip()
		# handle hashtag
		hashtag = data[2].strip()
		split_hash = hashtag.split('#')
		# gets rid of initial empty string for '#'
		split_hash = split_hash[1:]
		for s in split_hash:
			if len(s) > 14 or s == 'ALL':
				# (8)
				print(ILLEGAL_HASHTAG)
				return
		if len(split_hash) > 5:
			# (8)
			print(ILLEGAL_HASHTAG)
			return
		elif '##' in hashtag:
			# (8)
			print(ILLEGAL_HASHTAG)
			return
		elif re.search(r'[^a-zA-Z0-9#]', hashtag):
			# (8)
			print(ILLEGAL_HASHTAG)
			return
		else:
			# sent cmd
			tweetbody = [tweet, split_hash]
			tweetbody = json.dumps(tweetbody)
			tweetbody = "0" + tweetbody
			clientSocket.send(tweetbody.encode())
			return

	while True:
		# get user command
		prompt = input()
		# split prompt by quotes, gets each parameter
		data = prompt.split()
		# check that a prompt was entered
		if data is None:
			# (5)
			print('wrong number of parameters, connection refused.')
		# command is first argument
		cmd = data[0]
		if cmd == 'tweet':
			# split to get actual tweet
			data = prompt.split('"')
			# check that we have 3 arguments
			if len(data) == 3:
				ttweet(data)
		elif cmd == 'subscribe':
			if len(data) == 2:
				hashtag = data[1].strip()
				split_hash = hashtag.split('#')
				# handle hashtag errors in client input format
				# server will handle if hashtag is already subscribed to
				# or user at max subs
				if len(hashtag) > 15:
					print(ILLEGAL_HASHTAG)
				elif len(split_hash) > 2:
					print(ILLEGAL_HASHTAG)
				# re givin me problems for some reason
				# elif re.search(r'[^a-zA-Z0-9#', hashtag):
				# 	print("in3")
				# 	print('hashtag illegal format, connection refused.')
				else:
					half = hashtag[1:]
					msg = "1" + half
					clientSocket.send(msg.encode())
		elif cmd == 'unsubscribe':
			if len(data) == 2:
				hashtag = data[1].strip()
				split_hash = hashtag.split('#')
				# handle hashtag errors in client input format
				# server will handle if hashtag is already subscribed to
				# or user at max subs
				if len(hashtag) > 15:
					print(ILLEGAL_HASHTAG)
				elif len(split_hash) > 2:
					print(ILLEGAL_HASHTAG)
				# re givin me problems for some reason
				# elif re.search(r'[^a-zA-Z0-9#', hashtag):
				# 	print("in3")
				# 	print('hashtag illegal format, connection refused.')
				else:
					msg = "2" + hashtag[1:]
					clientSocket.send(msg.encode())
		elif cmd == 'timeline':
			if len(data) == 1:
				for tweet in timeline:
					print(tweet)
		elif cmd == 'getusers':
			if len(data) == 1:
				msg = "3getusers"
				clientSocket.send(msg.encode())
		elif cmd == 'gettweets':
			if len(data) == 2:
				usr = data[1]
				clientSocket.send(("4" + usr).encode())
		elif cmd == 'exit':
			clientSocket.send("5".encode())
			clientSocket.close()
			# (2)
			print(EXIT_SUCCESS)
			sys.exit()
			break
		## DELETE ##
		elif cmd == 'adminserverclose':
			msg = "*adminserverclose*"
			clientSocket.send(msg.encode())
			exit()
		## END DELETE ##
		else:
			print('command invalid, try again.')

def clientListen(clientSocket):
	while True:
		try:
			# 3 cases: sub success or error, tweet, or list of users

			msg = clientSocket.recv(1024).decode()
			cmd = msg[0]

			# server is sending tweet blast

			if cmd == "0":
				tweet = msg[1:]
				timeline.append(tweet)
				print(tweet)

			# server is sending sub or unsub status

			elif cmd == "1":
				print(msg[1:])
			elif cmd == "2":
				print(msg[1:])

			# server is sending list of users

			elif cmd == "3":
				users = json.loads(msg[1:])
				for u in users:
					print(u)
			elif cmd == "4":
				tweets = json.loads(msg[1:])
				for t in tweets:
					print(t)
			elif cmd == "7":
				print(msg[1:])
		except Exception as e:
			pass

def validIP(ipAddress):
	if ipAddress == 'localhost':
		return True
	check = ipAddress.split('.')
	if len(check) != 4:
		return False
	for num in check:
		if int(num) < 0 or int(num) > 255:
			return False
		# Add additional checks for ranges?
	return True

if __name__ == '__main__':
	main(sys.argv)
