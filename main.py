from Map import Map
from Location import Location
import pygame
import time
import os
import random
import math

from constants import *
from creatures import *

win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF, 32)
clock = pygame.time.Clock()


gamerules = {
    "#Grass": 200,
    "#Rabbit": 20,
    "#Fox": 20,

    "#Water": 0,
    "#Valley": 0,

    "MaxGrass": 2000,
    "GrassDistance": 3
}


def spawnCreatures():
    while gamerules["#Grass"] > 0:
        gLocation = Location(random.randrange(SQUARECOUNT),
                             random.randrange(SQUARECOUNT))
        rLocation = Location(random.randrange(SQUARECOUNT),
                             random.randrange(SQUARECOUNT))
        fLocation = Location(random.randrange(SQUARECOUNT),
                             random.randrange(SQUARECOUNT))

        if gamerules["#Grass"] != 0:
            gridSquare = Map.get_location(gLocation)
            if gridSquare.get_terrain().get_id() == 0 and gridSquare.get_terrain().get_sub_id() == 0 and len(gridSquare.get_creature_list()) == 0:
                Map.update(Grass(gLocation))
                print(f"GRASSSSSSSS {gridSquare}")
                gamerules["#Grass"] -= 1

        if gamerules["#Rabbit"] != 0:
            gridSquare = Map.get_location(rLocation)
            if gridSquare.get_terrain().get_id() == 0 and len(gridSquare.get_creature_list()) == 0:
                Map.update(Rabbit(rLocation))
                gamerules["#Rabbit"] -= 1

        if gamerules["#Fox"] != 0:
            gridSquare = Map.get_location(fLocation)
            if gridSquare.get_terrain().get_id() == 0 and len(gridSquare.get_creature_list()) == 0:
                Map.update(Fox(fLocation))
                gamerules["#Fox"] -= 1


def main():
    run = True

    Map.create()
    Map.draw(win)

    spawnCreatures()

    while run:

        clock.tick(5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run == False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run == False
                    pygame.quit()
                    quit()
        Map.iterate(win)
        pygame.display.update()


main()
