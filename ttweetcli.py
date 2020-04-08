from socket import *
import sys
from protocol import *
import json
import re
import threading
import time

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
	# NEED TO ERROR CHECK (1)
	serverName = args[1]

	# server port is the third argument
	serverPort = int(args[2])

	# username is fourth argument
	username = args[3]

	# checks that username only contains alphanumeric characters
	# (3)
	if re.search(r'[^a-zA-Z0-9]', username):
		print(INVALID_USERNAME)
		sys.exit()

	# creates client socket
	clientSocket = socket(AF_INET, SOCK_STREAM)

	# attempts to connect to server, exits if not found
	if clientSocket.connect_ex((serverName, serverPort)) != 0:
		print(INVALID_PORT)
		sys.exit()

	#check if username taken
	msg = "*USER*" + username
	clientSocket.send(msg.encode())
	val = clientSocket.recv(1024).decode()
	if val == "taken":
		# (4)
		print(USER_ALREADY_LOGGED_IN)
		sys.exit()
	else:
		# (1)
		print(LOGIN_SUCCESS)

	threading.Thread(target = sendThread, args = [clientSocket]).start()

def sendThread(clientSocket):

	listenThread = threading.Thread(target = clientListen, args = [clientSocket])
	listenThread.setDaemon(True)
	listenThread.start()

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
				if len(tweet) > 150:
					# (6)
					print(MSG_TOO_LONG)
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
				if len(split_hash) > 5:
					# (8)
					print(ILLEGAL_HASHTAG)
				elif '##' in hashtag:
					# (8)
					print(ILLEGAL_HASHTAG)
				elif re.search(r'[^a-zA-Z0-9#]', hashtag):
					# (8)
					print(ILLEGAL_HASHTAG)
				else:
					# sent cmd
					tweetbody = [tweet, split_hash]
					tweetbody = json.dumps(tweetbody)
					tweetbody = "*TWEET*" + tweetbody
					clientSocket.send(tweetbody.encode())
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
					msg = "*SUB*" + half
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
					msg = "*UNSUB*" + hashtag[1:]
					clientSocket.send(msg.encode())
		elif cmd == 'timeline':
			if len(data) == 1:
				for tweet in timeline:
					print(tweet)
		elif cmd == 'getusers':
			if len(data) == 1:
				users = clientSocket.recv(1024).decode()
				users = json.loads(users)
				for u in users:
					print(u)
		elif cmd == 'gettweets':
			if len(data) == 2:
				usr = data[1]
			print(cmd)
		elif cmd == 'exit':
			clientSocket.close()
			# (2)
			print(EXIT_SUCCESS)
			break
		else:
			print('command invalid, try again.')

def clientListen(clientSocket):
	while True:
		try:
			msg = clientSocket.recv(1024).decode()
			timeline.append(msg)
			print(msg)
		except Exception as e:
			pass



if __name__ == '__main__':
	main(sys.argv)
