from GridSquare import GridSquare
from Terrain import Terrain
from Location import Location
from constants import WIDTH, HEIGHT, GRIDSIZE, SQUARECOUNT
import math
import random
import pygame
import os

class Map:

    spawnable = set()

    map = [[GridSquare(Location(x, y)) for x in range(WIDTH // GRIDSIZE)]
           for y in range(HEIGHT // GRIDSIZE)]

    @staticmethod
    def iterate(window):
        # I don't like this, resets too often
        # Map.draw(window)
        # Move is a special function, we need to draw things moved
        # off of and onto, but only eat/repro on things moved onto
        Map.move()
        # Eat/repro shouldn't reset altered because theres no double iteration chance
        # assuming grass get switched around
        Map.eat()
        Map.reproduce()
        # Might need to happen before moving?
        Map.draw(window)

    @staticmethod
    def move():
        # Backup - set before iterating, through set when iterating should be the same
        # altered = GridSquare.reset_altered()
        # for gridSquare in altered:
        for gridSquare in GridSquare.reset_altered():
            creature_list = gridSquare.get_creature_list()
            for i, creature in enumerate(creature_list):
                location = creature.location
                gridSquare.delete_creature(creature)
                if creature.move(Map.get_surrounding_squares(location)):
                    Map.update(creature)

    @staticmethod
    def eat():
        for gridSquare in GridSquare.altered:
            creature_list = gridSquare.get_creature_list()[:]
            for creature in creature_list:
                eaten_creature = creature.eat(gridSquare.get_creature_list())
                if eaten_creature:
                    gridSquare.delete_creature(eaten_creature)

    @staticmethod
    def reproduce():
        for gridSquare in GridSquare.altered[:]:

            # Do we need to copy creature_list? besides (potentially) grass, there
            # shouldn't be anything that would be able to reproduce on the
            # same turn that it is created, right?

            # Might be needed if edit while looping error
            # creature_list = gridSquare.get_creature_list()[:]
            for creature in gridSquare.get_creature_list():
                location = creature.location
                creature.reproduce(Map.get_surrounding_squares(location))

    @staticmethod
    def draw(window):
        for gridSquare in GridSquare.altered:
            gridSquare.draw(window)

    @staticmethod
    def update(creature_container):
        if not isinstance(creature_container, (list, tuple)):
            creature_container = [creature_container]
        for creature in creature_container:
            Map.get_location(creature.location).add_creature(creature)

    @staticmethod
    def get_surrounding_squares(location):
        x, y = location.get_location()
        output = [[], [], [], []]

        if x > 0:
            output[0] = Map.get_location(
                Location(x - 1, y))
        if x < SQUARECOUNT - 1:
            output[1] = Map.get_location(
                Location(x + 1, y))
        if y > 0:
            output[2] = Map.get_location(
                Location(x, y - 1))
        if y < SQUARECOUNT - 1:
            output[3] = Map.get_location(
                Location(x, y + 1))

        #print(output)

        return output

    @staticmethod
    def get_location(location):
        x, y = location.get_location()
        if x < 0 or x >= SQUARECOUNT or y < 0 or y >= SQUARECOUNT:
            raise IndexError(
                f"Tried to get a square out of bounds: ({x}, {y})")
        return Map.map[y][x]

    def __str__(self):
        output = ""
        for row in self.map:
            output += " ".join([gridSquare.get_terrain()
                                for gridSquare in row])
            output += "\n"
        return output

    # TODO: Recode these in a better/cleaner/more efficient way

    @staticmethod
    def generate_struct(number_of_structs, terrain_id, min_count, max_count, threshold, count=0):
        for i in range(number_of_structs):
            initial_location = Location(random.randrange(
                0, SQUARECOUNT - 1), random.randrange(0, SQUARECOUNT - 1))
            Map.grow_struct(initial_location, terrain_id,
                            min_count, max_count, threshold)

    @staticmethod
    def grow_struct(initial_location, terrain_id, min_count, max_count, threshold, count=0):
        count += 1
        surrounding_squares = []
        # Check a 3x3 radius around the current square
        directions = [0]
        for i in range(3):
            directions += [-i, i]

        for i in directions:
            for j in directions:
                location = initial_location + (i, j)
                if location.get_x() < 0 or location.get_x() >= SQUARECOUNT or location.get_y() < 0 or location.get_y() >= SQUARECOUNT:
                    continue
                square = Map.get_location(location)
                terrain = square.get_terrain().get_id()

                # If about to touch a different type of terrain, return
                if terrain == terrain_id: continue
                if terrain_id == 1:
                    Map.spawnable.add(square)
                if terrain != 0: return False

                if abs(i) < 3 and abs(j) < 3:
                    # Add everything within a 2x2 area
                    surrounding_squares.append((square, location))

        # For each square within a 2x2 area
        for square, location in surrounding_squares:
            # Randomly skip, if about min count, or skip if above max count
            if (random.random() < threshold and count > min_count) or count > max_count or square.get_terrain().get_id() == terrain_id:
                continue
            if terrain_id == 1 and count <= min_count:
                square.set_terrain(terrain_id, 1)
            else:
                square.set_terrain(terrain_id)

            if square in Map.spawnable: Map.spawnable.remove(square)
            # Recursively grow for each block, and return false if it ends early
            if Map.grow_struct(location, terrain_id, min_count, max_count, threshold, count) == False:
                return False
        return True

    # Generates valleys onto the map
    @staticmethod
    def generate_valleys(valley_count=2):
        Map.generate_struct(valley_count, 2, 2, 4, 0.8)

    # Generates lakes onto the map
    @staticmethod
    def generate_lakes(lake_count=4):
        Map.generate_struct(lake_count, 1, 4, 8, 0.9)

    @staticmethod
    def create():
        Map.generate_lakes()
        Map.generate_valleys()

        for sq in Map.spawnable:
            sq.terrain = Terrain(0, 1)
