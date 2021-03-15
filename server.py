import socket
import select
import traceback
import sys
import time

ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

Server_IP = socket.gethostbyname(socket.gethostname())
Port = 8002
#find IP

try:
	ss.bind((Server_IP, Port))
	print('Running Server in: ', Server_IP, Port)

except:
	traceback.print_exc()
	print('Error_bind()')

ss.listen(20)


rlist = [ss, sys.stdin]
room_list = []


while True:
	#Get Information and Input Command stimultaneously
	R,W,X = select.select(rlist,[],[],50)

	for r in R:
		if r == ss:
			#if new Client Connected, send message that connected to the server
			newClient, newClientAddr = ss.accept()

			print('new client connected ', newClientAddr)
			msg = 'hello new client?'
			en_msg = msg.encode()
			newClient.send(en_msg)
			#add new client to the list
			rlist.append(newClient)
			
		elif r == sys.stdin:
			#input from server
			msg = sys.stdin.readline()

			#command list
			if msg[0] == '/':

				#Showing roomlist
				if msg == '/ls\n':
					print('Room List\n')
					for i in room_list:
						print('||',i[0],'||')

				#Destroying room
				elif msg[0:5] == '/kill':
					Room_To_Kill = msg[6:len(msg)-1]


					for i in room_list:
						if Room_To_Kill == i[0]:
							print('Room ' + i[0] + ' killed')
							#send the host that the room was destroyed by server
							victim = i[1][1]
							msg = '/KillbyServer'
							en_msg = msg.encode()
							victim.send(en_msg)
							break

				#Closing Server
				elif msg == '/exit\n':
					#Send Clients messge to close the program
					msg = '/C1ose'
					en_msg = msg.encode()
					#close the socket
					for i in rlist[2:]:
						i.send(en_msg)
						i.close()

					print("server closing")
					time.sleep(3)
					sys.exit()

				#if Unexpected Command
				else:
					print('Inappropriate Command')


			else:
				print('Inappropriate Command')

		else:
			#get message from hosts
			msg = r.recv(1024)
			de_msg = msg.decode()

			if (msg != b''):
				if de_msg[0] == '/':
					msplit = de_msg.split()

					#If Client send /ls message
					if de_msg == '/Sls':
						msg = 'Room List\n'

						for i in room_list:
							msg = msg + "||" + i[0] + "||\n"

						en_msg = msg.encode()
						r.send(en_msg)

					#If Client exits program
					elif de_msg == '/Cexit':
						for i in rlist[2:]:
							if r == i:
								print('Client has left')
								#remove client who left
								r.close()
								rlist.remove(i)

					#If client create the room
					elif msplit[0] == '/Rcreate':

						New_room = msplit[1]

						#Verifying the roomname
						al_ex = 0
						for i in room_list:
							if i[0] == New_room:
								al_ex = 1
								break

						if al_ex == 1:
							msg = '/fail'
							en_msg = msg.encode()
							r.send(en_msg)

						#If success making room, add to room_list
						else:
							room_list.append([New_room, ('host' , r)])
							msg = '/success'
							print('New room [', New_room, '] created')
							en_msg = msg.encode()
							r.send(en_msg)

					#If lient want to join
					elif msplit[0] == '/Cjoin':
						joinroom = msplit[1]
						joinnick = msplit[2]

						J_M = (msplit[2], r)

						ex_room = False
						Jmsg = ' '
						#Find room
						for i in room_list:
							if i[0] == joinroom:
								ex_room = True
								#Check Nickname
								if joinnick == 'UnKnown':
									i.append(J_M)
								else:
									Overlap = False
									for j in i[1:]:
										if j[0] == joinnick:
											Jmsg = '/Conflict'
											Overlap = True
											break

									if Overlap == False:
										i.append(J_M)
										Jmsg = '/Joining ' + joinroom
						#if there is no room
						if ex_room == False:
							Jmsg = '/Noroom'

						en_msg_J = Jmsg.encode()
						r.send(en_msg_J)

					#if Room Host lefted the room
					elif msplit[0] == '/Hleft':

						for j in range(len(room_list)):
							if room_list[j][1][1] == r:
								for i in room_list[j][2:]:
									msg = '/MCleft'
									en_msg = msg.encode()
									i[1].send(en_msg)
								#delete the room
								room_list.remove(room_list[j])
								break


					#if client lefted the room
					elif msplit[0] == '/Cleft':
						for j in range(len(room_list)):
							for i in room_list[j][1:]:
								if i[1] == r:
									#delete the client in the roomlist
									room_list[j].remove(i)
									break

					#if client want to whisper
					elif msplit[0] == '/W':
						Nick_Name = msplit[1]
						msg = msplit[2].split('/')
						#check room
						for j in range(len(room_list)):
							for i in room_list[j][1:]:
								if i[1] == r:
									#check sender
									sender = i[0]

									for k in room_list[j][1:]:
										#check receiver
										if k[0] == Nick_Name:
											_msg = ''
											for l in msg:
												_msg = _msg + ' ' + l

											msg = '(whisper from) ' + sender + ' : ' + _msg
											en_msg = msg.encode()
											k[1].send(en_msg)

						else:
							pass

				#broadcast the messages
				else:
					en_msg = de_msg.encode()
					#find message sender's room
					Send_msg = False
					for j in range(len(room_list)):

						for i in room_list[j][1:]:
							if i[1] == r:
								Send_msg = True
								break
						#Send message to the room member
						if Send_msg == True:
							for i in room_list[j][1:]:
								if i[1] != r:
									i[1].send(en_msg)

							break



#					room_list[[room_name, (host,_r), (nickname, r),...],[]]
