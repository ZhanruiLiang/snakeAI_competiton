import pygame
import socket
import config
import sys
import bz2
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

	----call by client program----------------------
	sync()
	sendCommand(direction): send out the direction you want to go
	connect(server): connect to the server
	join(player): join the game, seperate connect and join because client can be a audience.
	
	"""
	LEFT, DOWN, RIGHT, UP = 0, 1, 2, 3
	FOOD = Field.FOOD
	BODY = Field.BODY
	HEAD = 'head'
	BLOCK = Field.BLOCK
	EMPTY = 'empty'
	dirs = Field.dirs

	def __init__(self, server=None):
		""" initialize objects, if has server param passed, connect to server"""
		self._snakes = []
		self._foods = []
		self._blocks = []
		self._board = {}
		self._player = None
		self._id = None
		self._round = None
		self._last_round = None
		if server:
			self.connect(server)

	def connect(self, server):
		""" connect to server """
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((server, config.client_port))
		msg = self._send("{'cmd':'add'}")
		if msg['cmd'] == 'success':
			self._id = msg['id']
			print 'synced'
			self.sync()
		else:
			raise Exception(repr(msg))

	def join(self, player):
		""" join the player to the game, aka. request the server to add a snake."""
		msg = self._send("{'cmd':'join','id':%d, 'name':'%s'}"%(self._id, player.name))
		if msg['cmd'] == 'success':
			self._player = player
		else:
			print msg['reason']
			raise

	def quit(self):
		""" player quit the game, be continue watching, use method disconnect if want to compeletely exit the client. """
		self._send("{'cmd':'quit', 'id':%s}" % self._id)
		self._player = None

	def disconnect(self):
		""" leave the server. If not quit, then quit before leave. """
		if self._player:
			self.quit()
		self._send("{'cmd':'leave', 'id':%d}" % self._id)
		self.sock.close()

	def _send(self, msg):
		""" send a message to server, and return the result. """
		self.sock.send(msg)
		result = self.sock.recv(config.data_maxsize)
		result = eval(result, {'__buildin__':None, 'Statistic':Statistic}, {})
		return result

	def sync(self):
		# TODO, this implement is too ugly and slow...
		msg = self._send("{'cmd':'sync', 'id':%d}"%self._id)
		if msg['cmd'] == 'sync_info':
			info = eval(bz2.decompress(msg['info']), {'__buildin__':None, 'Statistic':Statistic}, {})
			self.size = info['size']
			self._foods = info['foods']
			self._blocks = info['blocks']
			self._snakes = []

			for s in info['snakes']:
				self._snakes.append(RenderSnake(s['name'], s['body'], s['direction'], s['stat']))

			if self._player:
				for s in self._snakes:
					if s.name == self._player.name:
						self._player.body = s.body
						break
				else:
					self._player = None

			self._round = info['round']
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
			# print self._last_round, self._round
			if self._last_round == None or self._last_round != self._round:
				# get into a new round
				if self._player:
					command = self._player.response()
					self.sendCommand(command)
					self._last_round = self._round
		elif msg['cmd'] == 'waiting':
			pass
		else:
			print msg['reason']
			raise

	def sendCommand(self, direction):
		""" Send to responsed command to the server. """
		msg = self._send("{'cmd':'response', 'id':%d, 'round':%d, 'direction':%s}"%(self._id, self._round, direction))
		if msg['cmd'] == 'success':
			pass
		else:
			print >> sys.stderr, 'Warning: current round is %d, not %d'%(msg['round'],self._round)

	def getContentAt(self, pos):
		try:
			return self._board[pos]
		except:
			return self.EMPTY
