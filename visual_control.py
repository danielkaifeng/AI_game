import game
import random
import numpy as np
import time

class game_agent():
	def start(self):
		space = game.SpaceGameWindow(num_monsters = 1, visible = True)
		while True:
			x_speed = 2*random.randint(0,1) - 1
			y_speed = 0.1

			if x_speed == 1:
				for i in range(80):
					done = space.main_loop(0.2 * x_speed, y_speed)
			else:
				for i in range(5):
					done = space.main_loop(x_speed, y_speed)

			time.sleep(2)	

			if done:
				space.close()
				break


if __name__ == "__main__":
	agent = game_agent()
	agent.start()
