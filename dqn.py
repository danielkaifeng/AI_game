# -*- coding: utf-8 -*-
import random
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense, Dropout, Reshape, Conv2D, MaxPool2D
from keras.layers import LSTM, Embedding

from keras.optimizers import Adam
import os
import game


EPISODES = 100000
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class DQNAgent:
	def __init__(self, state_size, action_size, chl):
		self.state_size = state_size
		self.action_size = action_size
		self.memory = deque(maxlen=5000)
		self.gamma = 0.95	# discount rate
		self.epsilon = 0.3	# exploration rate
		self.epsilon_min = 0.01
		self.epsilon_decay = 0.992
		self.learning_rate = 0.001
		self.channel = chl
		self.model = self._build_model()

	def _build_model(self):
		# Neural Net for Deep-Q learning Model
		dropout = 0.2
		model = Sequential()
		model.add(Dense(256, input_shape=[self.state_size, self.channel], activation='relu'))
		model.add(Dense(128, activation='relu'))
		model.add(Dropout(dropout))
		
		#model.add(LSTM(units=64, input_shape=[self.state_size,2], return_sequences=True))
		#model.add(LSTM(units=32, return_sequences=True))
		"""
		model.add(Reshape((self.state_size, 1, 256)))	
		model.add(Conv2D(filters=128, kernel_size=(5,1), padding='same', activation='relu'))
		model.add(Conv2D(filters=128, kernel_size=(5,1), padding='same', activation='relu'))
		model.add(MaxPool2D(pool_size=(2,1),padding='same'))
		model.add(Dropout(dropout))
		model.add(Conv2D(filters=128, kernel_size=(5,1), padding='same', activation='relu'))
		model.add(Conv2D(filters=128, kernel_size=(5,1), padding='same', activation='relu'))
		model.add(MaxPool2D(pool_size=(2,1),padding='same'))
		model.add(Dropout(dropout))
		"""

		model.add(Reshape((self.state_size*128,)))	

		model.add(Dense(256, activation='relu'))
		model.add(Dropout(dropout))
		model.add(Dense(128, activation='relu'))
		model.add(Dropout(dropout))

		#model.add(Reshape((2, (self.state_size/2)*64)))
		#model.add(Reshape((2, 256)))
		model.add(Dense(self.action_size, activation='linear'))
		model.compile(loss='mse',
					  optimizer=Adam(lr=self.learning_rate))
		return model

	def remember(self, state, action, reward, next_state, done):
		self.memory.append((state, action, reward, next_state, done))

	def act(self, state, time):
		if np.random.rand() <= self.epsilon:
			return random.randrange(3)
		act_values = self.model.predict(state)

		if time % 10 == 1:
			print '\n~~~~~~~~~~~~~action~~~~~~~~~~~~'
			print np.argmax(act_values[0]) - 1
			print act_values[0]
		return np.argmax(act_values[0])  # returns action direction

	def replay(self, batch_size):
		minibatch = random.sample(self.memory, batch_size)
		for state, action, reward, next_state, done in minibatch:
			target = reward
			if not done:
				target = (reward + self.gamma *
						  np.amax(self.model.predict(next_state)[0]))
			target_f = self.model.predict(state)
			target_f[0][action] = target
			self.model.fit(state, target_f, epochs=1, verbose=0)
		if self.epsilon > self.epsilon_min:
			self.epsilon *= self.epsilon_decay

	def load(self, name):
		self.model.load_weights(name)

	def save(self, name):
		self.model.save_weights(name)


if __name__ == "__main__":
	state_size = 16
	channel = 2
	action_size = 3
	agent = DQNAgent(state_size, action_size, channel)
	agent.load("./save/dodge-dqn.h5")
	done = False
	batch_size = 128


	for e in range(EPISODES):
		while True:
			space = game.SpaceGameWindow(num_monsters = state_size)
			init_act = random.randrange(3)-1
			state, _, done = space.main_loop(init_act)
			state /= 100

		 	if not done:
				break
			else:
				#print 'init done~~~~~~~~~~~~~~~~~~~~~~~~~~~'
				space.close()
			
		state = np.reshape(state, [1, state_size, channel])

		for time in range(1000):
			action = agent.act(state, time)

			next_state, reward, done = space.main_loop(2*(action-1))
			next_state /= 100

			if time % 50 == 0 and time > 1000:
				print next_state[2:20]
			#reward = 4*reward - np.sum(abs(action-1)) if not done else -30
			reward = reward if not done else -30
			next_state = np.reshape(next_state, [1, state_size, channel])
			agent.remember(state, action, reward, next_state, done)
			state = next_state
			if done:
				print("episode: {}/{}, score: {}, e: {:.2}"
					  .format(e, EPISODES, time, agent.epsilon))
				space.close()
				break

		space.close()

		if len(agent.memory) > batch_size:
			agent.replay(batch_size)
		if e % 20 == 0:
			print '\nsaving checkpoint file...\n'
			agent.save("./save/dodge-dqn.h5")
