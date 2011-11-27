import pygame
import socket
import config
import sys
from snake import RenderSnake
from baseobj import *
from field import Statistic, Field

class FieldClient(object):
	"""
	members:
	----access by user
	FOOD  --|
	HEAD  --|-- constants
	BODY  --|
	BLOCK --|
	dirs  --|
	size

	----access by system----------------------------
	_snakes
	_foods
	_blocks
	_board

	------------------------------------------------
	methods:
	----call by user--------------------------------
	getContentAt(pos): return the content at pos
	sendCommand(direction): send out the direction you want to go

	----call by client program----------------------
	sync()
	connect(server): connect to the server
	join(player): join the game, seperate connect and join because client can be a audience.
	
	"""
	FOOD = Field.FOOD
	BODY = Field.BODY
	HEAD = 'head'
	BLOCK = Field.BLOCK
	EMPTY = 'empty'
	dirs = Field.dirs

	def __init__(self, server=None):
		self._snakes = []
		self._foods = []
		self._blocks = []
		self._board = {}
		self._player = None
		self._id = None
		self._round = None
		if server:
			self.connect(server)

	def connect(self, server):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((server, config.client_port))
		msg = self._send("{'cmd':'add'}")
		if msg['cmd'] == 'success':
			self._id = msg['id']
			self.sync()
		else:
			raise Exception(repr(msg))

	def join(self, player):
		self._player = player
		msg = self._send("{'cmd':'join','id':%d, 'name':'%s'}"%(self._id, player.name))
		if msg['cmd'] == 'success':
			pass
		else:
			print msg['reason']
			raise

	def quit(self):
		"player quit the game, be continue watching"
		self._send("{'cmd':'quit', 'id':%s}" % self._id)
		self._player = None

	def disconnect(self):
		"leave the server"
		self._send("{'cmd':'leave', 'id':%d}" % self._id)
		self.sock.close()

	def _send(self, msg):
		self.sock.send(msg)
		result = eval(self.sock.recv(config.data_maxsize), {'__buildin__':None, 'Statistic':Statistic}, {})
		return result

	def sync(self):
		msg = self._send("{'cmd':'sync', 'id':%d}"%self._id)
		if msg['cmd'] == 'sync_info':
			self.size = msg['size']
			self._foods = msg['foods']
			self._blocks = msg['blocks']
			self._snakes = []

			for s in msg['snakes']:
				self._snakes.append(RenderSnake(s['name'], s['body'], s['direction'], s['stat']))

			if self._player:
				for s in self._snakes:
					if s.name == self._player.name:
						self._player.body = s.body
						break
				else:
					self._player = None

			round0 = self._round
			self._round = msg['round']
			self._board = {}
			board = self._board
			for x in self._foods:
				board[x] = self.FOOD
			for x in self._blocks:
				board[x] = self.BLOCK

			for s in self._snakes:
				for x in s.body:
					board[x] = self.BODY
				board[s.body[0]] = self.HEAD
			# test if this player lost
			if 'youlost' in msg:
				self.quit()

			# ask player to response
			if round0 == 0 or round0 != self._round:
				# get into a new round
				if self._player:
					command = self._player.response()
					self.sendCommand(command)
		elif msg['cmd'] == 'waiting':
			pass
		else:
			print msg['reason']
			raise
				
	def sendCommand(self, direction):
		msg = self._send("{'cmd':'response', 'id':%d, 'round':%d, 'direction':%s}"%(self._id, self._round, direction))
		if msg['cmd'] == 'success':
			pass
		else:
			raise Exception(repr(msg))

	def getContentAt(self, pos):
		try:
			return self._board[pos]
		except:
			return self.EMPTY
