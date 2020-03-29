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
		print(data) 
		# check that a prompt was entered
		# if data is None:
			# (5)
			# print('wrong number of parameters, connection refused.')
		# command is first argument
		cmd = data[0]
		if cmd == 'tweet':
			data = prompt.split('"')
			if len(data) == 3:
				clientSocket.send(cmd.encode())
				tweet = data[1]
				if len(tweet) > 150:
					print("message length illegal, connection refused.")
				clientSocket.send(tweet.encode())
				hashtag = data[2]
			print(cmd)
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
				print(cmd)
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