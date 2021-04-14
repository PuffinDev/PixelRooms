from network import Network
import random
import os
import pygame as pg
import threading
from time import sleep, time

game_config = {}

with open("game.config", "r") as f:
    for line in f:
        key, value = line.split("=")
        game_config[key] = value

try:
    HOST = game_config["ip"]
    PORT = game_config["port"]
    ADDR = (HOST.strip(), int(PORT))
except: 
    print("[ERROR] Failed to read values from game.config")
    exit()


WIDTH = 1200
HEIGHT = 700

PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60

pg.font.init()
NAME_FONT = pg.font.SysFont(None, 24)

win = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Pixel Rooms alpha")

players = []

running = True


def draw(players, clock, ping, debug=True):

    win.fill((254, 255, 250))

    #Render players
    for player in players:
        p = players[player]
        pg.draw.rect(win, p["color"], (p["x"], p["y"], PLAYER_WIDTH, PLAYER_HEIGHT))

        img = NAME_FONT.render(p["name"], True, (0,0,0))
        win.blit(img, (p["x"], p["y"] - PLAYER_HEIGHT / 2))

    #Render debug info
    img = NAME_FONT.render("FPS: " + str(int(clock.get_fps())), True, (0,0,0))
    win.blit(img, (0,0))
    img = NAME_FONT.render("PING: " + str(round(ping)) + "ms", True, (0,0,0))
    win.blit(img, (0,20))


    pg.display.update()


def main(playername):
    global players
    global running

    server = Network()
    server.setup(ADDR)
    id = server.connect(playername)
    vel = 4

    players = server.send("get")

    clocc = pg.time.Clock()

    while running:
        clocc.tick(60)

        player = players[id]

        keys = pg.key.get_pressed()

        if keys[pg.K_a]:
            player["x"] = player["x"] - vel
        if keys[pg.K_d]:
            player["x"] = player["x"] + vel
        if keys[pg.K_w]:
            player["y"] = player["y"] - vel
        if keys[pg.K_s]:
            player["y"] = player["y"] + vel

        #Send position data
        data = "move " + str(player["x"]) + ' ' + str(player["y"])
        start = round(time() * 1000) #convert to ms
        players = server.send(data) #Time it to calculate ping
        end = round(time() * 1000)
        ping = (end - start)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                pg.quit()

        draw(players, clocc, ping)

main(input("Choose a name >> "))
