import pygame
import socket
import config
import sys
import bz2
import xmlrpclib
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
		""" connect to server, and sync for the first time """
		self.server = xmlrpclib.ServerProxy('http://%s:%d/'%(server, config.server_port), allow_none=True)
		succ, msg = self.server.add()
		if succ:
			self._id = msg
			print 'sync first time'
			self.sync()
		else:
			# fail to connect server, should raise error
			raise Exception("Fail to connect server %s"%(server))

	def join(self, player):
		""" join the player to the game, aka. request the server to add a snake."""
		succ, msg = self.server.join(self._id, player.name)

		if succ:
			self._player = player
		else:
			raise Exception(msg)

	def quit(self):
		""" player quit the game, be continue watching,
		use method disconnect if want to compeletely exit the client. """
		succ, msg = self.server.quit(self._id)

		self._player = None

	def disconnect(self):
		""" leave the server. If not quit, then quit before leave. """
		if self._player:
			self.quit()
		succ, msg = self.server.leave(self._id)

	def sync(self):
		succ, msg = self.server.sync(self._id)
		if succ:
			info = msg['info']
			self.size = info['size']
			self._foods = map(tuple, info['foods'])
			self._blocks = map(tuple, info['blocks'])
			self._snakes = []

			for s in info['snakes']:
				# self._snakes.append(RenderSnake(s['name'], s['body'], s['direction'], s['stat']))
				# TODO add stat back
				self._snakes.append(RenderSnake(s['name'], 
					[tuple(x) for x in s['body']], s['direction'], Statistic()))

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
				return

			# ask player to response
			# print self._last_round, self._round
			if self._last_round == None or self._last_round != self._round:
				# get into a new round
				if self._player:
					resp = self._player.response()
					self.sendResponse(resp)
					self._last_round = self._round
		else:
			raise Exception("Failed to sync with server, returned: %s"%str(msg))

	def sendResponse(self, direction):
		""" Send to responsed direction to the server. """
		succ, msg = self.server.response(self._id, self._round, direction)
		if not succ:
			print >> sys.stderr, 'Warning: current round is %d, not %d'%(msg['round'],self._round)

	def getContentAt(self, pos):
		try:
			return self._board[pos]
		except:
			return self.EMPTY
