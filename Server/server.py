import socket
import threading
import pickle
from time import sleep
import random
import math

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


PORT = 8080

FORMAT = 'utf-8'

WIDTH, HEIGHT = 1200, 700

HOST_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(HOST_NAME)

# try to connect to server
try:
    s.bind((SERVER_IP, PORT))
except socket.error as e:
    print(str(e))
    print("[ERROR] Failed to start server")
    quit()

s.listen()

print(f"[SERVER] Server is running on {SERVER_IP}")

players = {}
connections = 0
client_id = 0


# FUNCTIONS

def get_start_location(players):

	x = random.randrange(0,WIDTH)
	y = random.randrange(0,HEIGHT)
	return (x,y)


def handle_client(conn, client_id):
	global connections, players

	current_id = client_id

	# recieve a name from the client
	data = conn.recv(16)
	name = data.decode(FORMAT)
	print("[LOG]", name, "connected to the server.")

	# Setup properties for each new player
	while True:
		r, g, b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
		if not r + g + b >= 720: #If color is too bright
			color = (r, g, b)
			break

	x, y = get_start_location(players)
	players[current_id] = {"x":x, "y":y,"color":color,"score":0,"name":name}  # x, y color, score, name

	conn.send(str.encode(str(current_id)))


	while True:
		try:
			# Recieve data from client
			data = conn.recv(32)

			if not data:
				break

			data = data.decode(FORMAT)

			if data.split(" ")[0] == "move":
				split_data = data.split(" ")
				x = int(split_data[1])
				y = int(split_data[2])
				players[current_id]["x"] = x
				players[current_id]["y"] = y

				send_data = pickle.dumps(players)

			elif data.split(" ")[0] == "id":
				send_data = str.encode(str(current_id))

			elif data.split(" ")[0] == "get":
				send_data = pickle.dumps(players)
				print(f"[SERVER] {name}#{client_id} Requested room data")
				print(players)
			else:
				send_data = pickle.dumps(players)

			# send data back to clients
			conn.send(send_data)

		except Exception as e:
			print(e)
			break

		sleep(0.001)

	# Client disconnected
	print(f"[DISCONNECT] {name}#{client_id} left the game")

	connections -= 1 
	del players[current_id]
	conn.close()

# Game loop

print("[SERVER] Waiting for connections")

while True:
	
	host, addr = s.accept()
	print("[NEW CONNECTION] Connected to:", addr)

	connections += 1
	thread = threading.Thread(target=handle_client, args=(host, client_id,))
	thread.start()
	client_id += 1
