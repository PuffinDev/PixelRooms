from network import Network
import random
import os
import pygame as pg
pg.font.init()
import threading
from time import sleep, time


WIDTH = 1200
HEIGHT = 700

PLAYER_WIDTH = 45
PLAYER_HEIGHT = 60

NAME_FONT = pg.font.SysFont(None, 24)


players = []
running = True

print("[LOADING] Loading game config...")
#LOAD GAME CONFIG
game_config = {}
with open("game.config", "r") as f:
    for line in f:
        key, value = line.split("=")
        value = value.strip()
        game_config[key] = value
try:
    HOST = game_config["ip"]
    PORT = game_config["port"]
    ADDR = (HOST, int(PORT))
except: 
    print("[ERROR] Failed to read values from game.config")
    exit()


# LOAD SKINS
print("[LOADING] Loading skins...")
skins = {}
for filename in os.listdir("skins/"):
    if filename.endswith(".png"):
        path = os.path.join("skins/", filename)
        name, extention = filename.split('.')
        skins[name] = pg.image.load(path)
        skins[name] = pg.transform.scale(skins[name], (PLAYER_WIDTH, PLAYER_HEIGHT))

#FUNCTIONS

def draw(players, clock, ping, id, debug=True):

    win.fill((254, 255, 250))

    #Render players
    for player in players:
        
        #Load and blit skin
        p = players[player]
        if p["skin"] in skins.keys(): 
            win.blit(skins[p["skin"]], (p["x"], p["y"]))
        elif "default_skin" in skins.keys():
            win.blit(skins["default_skin"], (p["x"], p["y"]))
            #print("[SERVER] Could not find skin '" + p["skin"] + "'. Using default skin.")
        else:
            exit()
            #print("[ERROR] Could not load 'skins/default_skin.png'")

        #Render name
        img = NAME_FONT.render(p["name"], True, (0,0,0))
        win.blit(img, (p["x"], p["y"] - PLAYER_HEIGHT / 2))

    #Render debug info
    img = NAME_FONT.render("FPS: " + str(int(clock.get_fps())), True, (0,0,0))
    win.blit(img, (0,0))
    img = NAME_FONT.render("PING: " + str(round(ping)) + "ms", True, (0,0,0))
    win.blit(img, (0,20))


    pg.display.update()


def main(playername, skin):
    global players
    global running

    print("[GAME] Connecting to server...")
    server = Network()
    server.setup(ADDR)
    id = server.connect(playername, skin)
    print("[GAME] Connected!")

    vel = 3

    players = server.send("get")

    clocc = pg.time.Clock()

    while running:
        clocc.tick(60)

        player = players[id]

        keys = pg.key.get_pressed()

        if keys[pg.K_a] or keys[pg.K_LEFT]:
            if player["x"] > 0:
                player["x"] = player["x"] - vel
        
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            if player["x"] + PLAYER_WIDTH < WIDTH:
                player["x"] = player["x"] + vel
        
        if keys[pg.K_w] or keys[pg.K_UP]:
            if player["y"] > 0:
                player["y"] = player["y"] - vel
        
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            if player["y"] + PLAYER_HEIGHT < HEIGHT:
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

        draw(players, clocc, ping, id)


win = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Pixel Rooms alpha")


main(input("Choose a name >> "), game_config["skin"])
