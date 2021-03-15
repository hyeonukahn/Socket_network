import socket
import select
import traceback
import sys
import time

#Input server IP
Server_IP = input('Server IP : ')
Port = 8002
cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	cs.connect((Server_IP, Port))

except:
	print('There is no server to connect to')
	exit()

rlist = [cs,sys.stdin]
In_chat = False
R_host = False

while True:
	#Get Information and Input Command&message stimultaneously
	R,W,X = select.select(rlist,[],[],50)
	for r in R:

		if r == sys.stdin:
			msg = sys.stdin.readline()

			#Commands
			if msg[0] == '/':
				msplit = msg.split()

				#Show room list
				if msg == '/ls\n':
					msg = '/Sls'
					en_msg = msg.encode()
					cs.send(en_msg)

				#create the room
				elif msplit[0] == '/create':
					if In_chat == True:
						print('Cannot create: client is already in a chat room')

					else:
						if len(msplit) != 2:
							print('/create : /create [roomname]')

						else:
							msg = '/Rcreate ' + msplit[1]
							en_msg = msg.encode()
							cs.send(en_msg)

							recall_msg = cs.recv(1024).decode()
							#if the roomname is not overlap
							if recall_msg == '/success':
								print('room created')
								In_chat = True
								R_host = True
								Nick_Name = 'host'
							else:
								print('roomname already exists')

				#joining chatroom
				elif msplit[0] == '/join':
					#if already in chat state
					if In_chat == True:
						print('Cannot join:client is already in a chat room')

					else:
						if (len(msplit) > 4 or len(msplit) == 1):
							print('/join : /join [roomname] (nickname)')

						else:
							Room_Name = msplit[1]

							if len(msplit) == 2:
								Nick_Name = 'UnKnown'
							else:
								Nick_Name = msplit[2]

							#send roomname and Nickname
							msg = '/Cjoin ' + Room_Name + ' ' + Nick_Name
							en_msg = msg.encode()
							cs.send(en_msg)

							recall_msg = cs.recv(1024).decode()
							print(recall_msg)
							if recall_msg == '/Conflict':
								print('Cannot join:Nickname already exists')

							elif recall_msg == '/Noroom':
								print('There is no room with that name')

							else:
								print('joining room...', Room_Name)
								In_chat = True

					
				#client exit in room or program
				elif msg == '/exit\n':
					#in chat
					if R_host == True:
						msg = '/Hleft'
						en_msg = msg.encode()
						cs.send(en_msg)
						R_host = False
						In_chat = False

					elif In_chat == True:
						msg = '/Cleft'
						en_msg = msg.encode()
						cs.send(en_msg)

						print('Leaving Chatroom')
						In_chat = False
					#outchat
					else:
						msg = '/Cexit'
						en_msg = msg.encode()
						cs.send(en_msg)
						time.sleep(1)
						sys.exit()

				#Whisper
				elif msplit[0] == '/whisper':
					if In_chat == True:
						if len(msplit) < 3:
							print('/whisper : /whisper [nickname] [message]')

						else:
							reci = msplit[1]
							msg = ''
							for i in msplit[2:]:
								msg = msg + '/' + i
							#send the receiver and message information
							msg = '/W ' + reci + ' ' + msg
							en_msg = msg.encode()
							cs.send(en_msg)

					else:
						print('Not in Chatroom')

				#unexpected Command
				else:
					print('Inappropriate Command')

			else:
				#if chat state, send the message
				if In_chat == True:
					msg = Nick_Name + ' : ' + msg
					en_msg = msg.encode()
					cs.send(en_msg)

				else:
					print('Not in chatroom')

		#receiving part
		elif r == cs:
			msg = cs.recv(1024)

			if (msg != b''):
				de_msg = msg.decode()

				#receive the Command from server
				if de_msg[0] == '/':

					if de_msg == "/C1ose":
						sys.exit()

					elif de_msg == "/MCleft":
						print('Leaving Chatroom')
						In_chat = False

					elif R_host == True:
						if de_msg == '/KillbyServer':
							print('The room was killed by server')
							msg = '/Hleft'
							en_msg = msg.encode()
							cs.send(en_msg)
							R_host = False
							In_chat = False

					else:
						pass

				#print the message
				else:
					print(de_msg)

