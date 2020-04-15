Overview:
	We decided to implement the client side through two concurrent threads per client, one for sending and one for receiving. The sending thread takes in user input and sends it to the server, while the listening thread receives messages from the server and prints it to the console for commands like timeline, gettweets, getusers, and overall tweet notifications. The server side runs a separate thread for each client to allow for concurrent threading. The server stores dictionaries of relevant information, such as users, their connections, tweets, hashtags, and subscriptions. 
Team members:
	Raymond Bryant- Set up initial client and server skeleton code. Coded handling of user input and basic multithreading to handle multiple clients. 
	Ethan Sisk- Added onto user input handling and functionality, implemented select to ensure threads were nonblocking, implemented server side behavior for client input.
	Tyler Brazelton- Finalized protocol messages to match outputs. Added additional input checks, refactored client and server code, wrote scripts and other code for debugging, and fixed a few major bugs.  
How to use code:
	Simply run ttweetcli.py and ttweetser.py as the project PDF dictates. Run ttweetser.py with: python ttweetser.py <port number>, where port number is a valid port number for the server. Run ttweetcli.py with: python ttweetcli.py <IP> <port number> <username>, where IP is the IP address of the client, port number is a valid port number, and username is a valid username. 
Special Instructions:
	Make sure that protocol.py is in the same directory as ttweetcli.py and ttweetser.py, as it contains macros used in those files.
