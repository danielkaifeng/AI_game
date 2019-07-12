#!/usr/bin/env python

from pyglet import window
from pyglet import clock
from pyglet import font
from pyglet import image

import numpy as np
import random
import os


def load_image(image_file_name):
	full_path = os.path.join('./data', image_file_name)
	return image.load(full_path)


class SpaceGameWindow(window.Window):
	def __init__(self, *args, **kwargs):
		self.max_monsters = 1
		#window.Window.__init__(self, *args, **kwargs)
		window.Window.__init__(self, 1600,800, visible=True)
		self.set_mouse_visible(False)
		self.init_sprites()

	def init_sprites(self):
		self.bullets = []
		self.monsters = []
		self.ship = SpaceShip(self.width - 150, 10, x=100 + self.width/2, y=self.height - 120)
		self.bullet_image = load_image("bullet.png")
		#self.monster_image = load_image("monster.png")
		self.monster_image = load_image("ball.png")

	def main_loop(self, x_speed, y_speed):
		x_out_of_boundary = self.ship.x < 0 or self.ship.x > self.width
		#self.has_exit = x_out_of_boundary or y_out_of_boundary
		if x_out_of_boundary:
			self.ship.x = 100

		self.create_monster()

		self.dispatch_events()
		self.clear()
		self.draw()

		self.update(x_speed, y_speed)

		#Tick the clock
		#clock.schedule_interval(self.create_monster, 0.3)
		clock.tick()
		#Gets fps and draw it
		#fps_text.text = ("fps: %d") % (clock.get_fps())
		#fps_text.draw()
		self.flip()

		self.create_monster()
		return self.has_exit

	def update(self, x_speed, y_speed):
		to_remove = []
		for sprite in self.monsters:
			sprite.update(x_speed, y_speed)
			#Is it dead?
			if (sprite.dead):
				to_remove.append(sprite)

		#Remove dead sprites
		for sprite in to_remove:
			self.monsters.remove(sprite)

		self.ship.update()
		#Is it dead?
		monster_hit = self.ship.collide_once(self.monsters)

		if (monster_hit is not None):
			self.ship.dead = True
			self.has_exit = True
			self.close()

	def draw(self):
		for sprite in self.bullets:
			sprite.draw()
		for sprite in self.monsters:
			sprite.draw()
		self.ship.draw()

	def create_monster(self):
		while (len(self.monsters) < self.max_monsters):
			self.monsters.append(Monster(self.monster_image, x=50, y=0))


class Sprite(object):
	def __get_left(self):
		return self.x
	left = property(__get_left)

	def __get_right(self):
		return self.x + self.image.width
	right = property(__get_right)

	def __get_top(self):
		return self.y + self.image.height
	top = property(__get_top)

	def __get_bottom(self):
		return self.y
	bottom = property(__get_bottom)

	def __init__(self, image_file, image_data=None, **kwargs):

		#init standard variables
		self.image_file = image_file
		if (image_data is None):
			self.image = load_image(image_file)
		else:
			self.image = image_data
		self.x = 0
		self.y = 0
		self.dead = False
		#Update the dict if they sent in any keywords
		self.__dict__.update(kwargs)

	def draw(self):
		self.image.blit(self.x, self.y)

	def update(self):
		pass

	def intersect(self, sprite):
		#Do the two sprites intersect?
		return not ((self.left > sprite.right)
			or (self.right < sprite.left)
			or (self.top < sprite.bottom)
			or (self.bottom > sprite.top))

	def collide(self, sprite_list):
		"""Determing ther are collisions with this
		sprite and the list of sprites
		@param sprite_list - A list of sprites
		@returns list - List of collisions"""

		lst_return = []
		for sprite in sprite_list:
			if (self.intersect(sprite)):
				lst_return.append(sprite)
		return lst_return

	def collide_once(self, sprite_list):
		"""Determine if there is at least one
		collision between this sprite and the list
		@param sprite_list - A list of sprites
		@returns - None - No Collision, or the first
		sprite to collide
		"""
		for sprite in sprite_list:
			if (self.intersect(sprite)):
				return sprite
		return None

class SpaceShip(Sprite):
	def __init__(self, text_x, text_y, **kwargs):
		Sprite.__init__(self, "white_goal.png", **kwargs)

	def draw(self):
		Sprite.draw(self)


class Monster(Sprite):
	def __init__(self, image_data, **kwargs):
		Sprite.__init__(self, "", image_data, **kwargs)

	def update(self, x_velocity, y_velocity):
		self.y += y_velocity
		self.x += x_velocity
		#Have we gone beneath the botton or the top of the screen?
		if (self.y < 0 or self.y>800):
			self.dead = True

	def get_position(self):
		return [self.x, self.y]

if __name__ == "__main__":
	space = SpaceGameWindow()
	while True:
		space.main_loop([1,1])

