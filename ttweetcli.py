from socket import *
import sys
import protocol
import json
import re

def main(args):

	# checks number of args
	if len(args) is not 4:
		# (5)
		print('wrong number of parameters, connection refused.')
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
		print('username has wrong format, connection refused.')

	# creates client socket
	clientSocket = socket(AF_INET, SOCK_STREAM)
	# attempts to connect to server, exits if not found
	if clientSocket.connect_ex((serverName, serverPort)) is not 0:
		print("server port invalid, connection refused.")
		sys.exit()

	# check if username is taken
	clientSocket.send(username.encode())
	val = clientSocket.recv(1024).decode()
	if val == "taken":
		# (4)
		print('username illegal, connection refused.')
		sys.exit()
	else:
		# (1)
		print('username legal, connection established.')

	# connection established with username
	while True:
		# get user command
		prompt = input()
		# split prompt by quotes, gets each parameter
		data = prompt.split()
		# check that a prompt was entered
		if data is None:
			(5)
			print('wrong number of parameters, connection refused.')
		# command is first argument
		cmd = data[0]
		if cmd == 'tweet':
			# split to get actual tweet
			data = prompt.split('"')
			# check that we have 3 arguments
			if len(data) == 3:
				# sent cmd
				clientSocket.send(cmd.encode())
				# handle message
				tweet = data[1]
				if tweet == None:
					# (7)
					print("message format illegal")
				if len(tweet) > 150:
					# (6)
					print("message length illegal, connection refused.")
				# handle hashtag
				hashtag = data[2].strip()
				split_hash = hashtag.split('#')
				# gets rid of initial empty string for '#'
				split_hash = split_hash[1:]
				if split_hash > 5:
					# (8)
					print('hashtag illegal format, connection refused.')
				for s in split_hash:
					if len(s) > 14:
						# (8)
						print('hashtag illegal format, connection refused.')
				if '##' in hashtag:
					# (8)
					print('hashtag illegal format, connection refused.')
				elif re.search(r'[^a-zA-Z0-9#]', hashtag):
					# (8)
					print('hashtag illegal format, connection refused.')
				tweetbody = [tweet, hashtag]
				tweetbody = json.dumps(tweetbody)
				clientSocket.send(tweetbody.encode('utf-8'))
		elif cmd == 'subscribe':
			if len(data) == 2:
				hashtag = data[1]
			print(cmd)
		elif cmd == 'unsubscribe':
			if len(data) == 2:
				hashtag = data[1]
			print(cmd)
		elif cmd == 'timeline':
			if len(data) == 1:
				print(cmd)
		elif cmd == 'getusers':
			if len(data) == 1:
				clientSocket.send(cmd.encode())
				users = clientSocket.recv(1024)
				for u in users:
					print(u)
		elif cmd == 'gettweets':
			if len(data) == 2:
				usr = data[1]
			print(cmd)
		elif cmd == 'exit':
			clientSocket.send(cmd.encode())
			clientSocket.close()
			# (2)
			print('bye bye')
			break
		else:
			print('command invalid, try again.')


if __name__ == '__main__':
	main(sys.argv)