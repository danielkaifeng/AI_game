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
		self.max_monsters = kwargs['num_monsters'] - 2
		#Let all of the standard stuff pass through
		#window.Window.__init__(self, *args, **kwargs)
		window.Window.__init__(self, 1600,700)
		self.set_mouse_visible(False)
		self.init_sprites()

	def init_sprites(self):
		self.bullets = []
		self.monsters = []
		self.ship = SpaceShip(self.width - 150, 10, x=self.width/2,y=100)
		self.bullet_image = load_image("bullet.png")
		self.monster_image = load_image("monster.png")

	def main_loop(self, action):
		x_move, y_move = action
		ship_pos = [self.ship.x + x_move, self.ship.y + y_move]

		x_out_of_boundary = ship_pos[0] > self.width or ship_pos[0] < 0
		y_out_of_boundary = ship_pos[1] > self.height or ship_pos[1] < 0

		self.has_exit = x_out_of_boundary or y_out_of_boundary
		#if x_out_of_boundary or y_out_of_boundary:
		#	self.ship.x = 400
		#	self.ship.y = 400

		#ft = font.load('Arial', 28)
		#fps_text = font.Text(ft, y=10)

		self.create_monster()
		clock.set_fps_limit(512)


		#while not self.has_exit:
		self.dispatch_events()
		self.clear()

		#update ship action,  bullet and monster
		self.update(ship_pos)
		self.draw()

		#Tick the clock
		clock.tick()
		#Gets fps and draw it
		#fps_text.text = ("fps: %d") % (clock.get_fps())
		#fps_text.draw()
		self.flip()

		self.create_monster()

		"""
		position = [[ship_pos[0], ship_pos[1]]]
		for sprite in self.monsters:
			pos = sprite.get_position()
			#pos[0] /= float(self.width)
			#pos[1] /= float(self.height)
			position.append(pos)
		"""
		position = []
		position.append(ship_pos + [np.sqrt(np.square(ship_pos[0])+np.square(ship_pos[1]))])
		p1 = [self.width - ship_pos[0], self.height - ship_pos[1]]
		p1.append(np.sqrt(np.square(p1[0])+np.square(p1[1])))
		position.append(p1)
		for sprite in self.monsters:
			pos = sprite.get_position()
			pos[0] -= ship_pos[0]
			pos[1] -= ship_pos[1]
			pos.append(np.sqrt(np.square(pos[0])+np.square(pos[1])))
			position.append(pos)

		reward = 1
		position = np.array(position)
		return (position, reward, self.has_exit)

	def update(self, pos):
		#x_move, y_move = (0.7 - np.random.random((2))) * (x_move, y_move)

		self.ship.x, self.ship.y = pos

		to_remove = []
		for sprite in self.monsters	:
			sprite.update()
			#Is it dead?
			if (sprite.dead):
				to_remove.append(sprite)
		#Remove dead sprites
		for sprite in to_remove:
			self.monsters.remove(sprite)

		#Bullet update and collision
		to_remove = []
		for sprite in self.bullets:
			sprite.update()
			if (not sprite.dead):
				monster_hit = sprite.collide_once(self.monsters)
				if (monster_hit is not None):
					sprite.on_kill()
					self.monsters.remove(monster_hit)
					to_remove.append(sprite)
			else:
				to_remove.append(sprite)
		#Remove bullets that hit monsters
		for sprite in to_remove:
			self.bullets.remove(sprite)

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
			self.monsters.append(Monster(self.monster_image, x=random.randint(0, self.width) , y=random.randint(10,self.height/20)*20))

	"""******************************************
	Event Handlers
	def on_mouse_motion(self, x, y, dx, dy):
		pass
	#	self.ship.x = x
	#	self.ship.y = y
                #print x,y

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.ship.x = x
		self.ship.y = y

	def on_mouse_press(self, x, y, button, modifiers):

		if (button == 1):
			self.bullets.append(Bullet(self.ship
					, self.bullet_image
					, self.height
					, x=x + (self.ship.image.width / 2) - (self.bullet_image.width / 2)
					, y=y))
	*********************************************"""

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

		self.kills = 0
		Sprite.__init__(self, "ship.png", **kwargs)

		#Create a font for our kill message
		self.font = font.load('Arial', 28)
		#The pyglet.font.Text object to display the FPS
		#self.kill_text = font.Text(self.font, y=text_y, x=text_x)

	def draw(self):
		Sprite.draw(self)
		#self.kill_text.text = ("Kills: %d") % (self.kills)
		#self.kill_text.draw()

	def on_kill(self):
		self.kills += 1


class Bullet(Sprite):

	def __init__(self, parent_ship, image_data, top, **kwargs):
		self.velocity = 5
		self.screen_top = top
		self.parent_ship = parent_ship
		Sprite.__init__(self,"", image_data, **kwargs)

	def update(self):
		self.y += self.velocity
		#Have we gone off the screen?
		if (self.bottom > self.screen_top):
			self.dead = True

	def on_kill(self):
		"""We have hit a monster let the parent know"""
		self.parent_ship.on_kill()

class Monster(Sprite):

	def __init__(self, image_data, **kwargs):
		self.y_velocity = 1
		self.set_x_velocity()
		self.x_move_count = 0
		self.x_velocity
		Sprite.__init__(self, "", image_data, **kwargs)

	def update(self):
		self.y -= self.y_velocity
		self.x += self.x_velocity#random.randint(-3,3)
		self.x_move_count += 1
		#Have we gone beneath the botton of the screen?
		if (self.y < 0):
			self.dead = True

		if (self.x_move_count >=30):
			self.x_move_count = 0
			self.set_x_velocity()

	def get_position(self):
		#return [self.x, self.y, self.x_velocity/3., self.y_velocity/3.]
		return [self.x, self.y]

	def set_x_velocity(self):
		self.x_velocity = random.randint(-3,3)

if __name__ == "__main__":
	space = SpaceGameWindow()
	while True:
		space.main_loop([1,1])

