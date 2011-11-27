import pygame
import itertools
import config
import sys
import select
import socket
from random import randint
from field import Field
from snake import *
from baseobj import *

X, Y = 0, 1
fSize = config.field_size1 # the field size

waited = 0
# to store the name of dead players, if that client send quit, remove the name 
# from here
ghosts = []


def initField(field):
	field.reset()

	# add block
	for i in xrange(fSize[0]):
		for j in xrange(fSize[1]):
			if i == 0 or i == fSize[0]-1 or j == 0 or j == fSize[1] - 1:
				field._addContentAt((i,j), Block())
	for y in xrange(3, 20, 7):
		for x in xrange(7, 18):
			field._addContentAt((x, y), Block())
	# add food
	for i in xrange(50):
		field._add_food()

def startServer():
	# return a socket obj as server
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	port = config.server_port
	# try:
	server.bind(('', port))
	# except socket.error as e:
	# 	print e
	# 	port += 1
	# 	if port - config.server_port > 10:
	# 		raise
	server.listen(config.server_backlog)
	return server

class IDGener:
	""" To generate id"""
	def __init__(self):
		self._ids = set()
	def gen(self):
		while 1:
			r = randint(100000, 999999)
			if r not in self._ids:
				self._ids.add(r)
				return r

msg_success = "{'cmd':'success'}"
def parseCommand(field, data, client):
	global clients, waited
	msg = eval(data, {'__buildin__':None}, {})
	cmd = msg['cmd']
	if cmd == 'add':
		id = id_gener.gen()
		clients[id] = [None, client]
		client.send("{'cmd':'success', 'id':%d}"%(id))
		print 'client #%s added into this server' % (id)

	if cmd == 'join':
		# generate an new id, bound it to the client
		id = msg['id']
		name = msg['name']
		clients[id] = [name, client]
		initpos, direction =  field.newInitPos()
		snake = BaseSnake(name, initpos, direction, field)
		field.register(snake)
		client.send(msg_success)
		print 'player %s joined the game' % (name)
	elif cmd == 'quit':
		# the player quit the game, but watching
		id = msg['id']
		name = clients[id][0]
		clients[id][0] = None
		if name in ghosts:
			ghosts.remove(name)
		print 'player %s quited the game' % (name)
	elif cmd == 'leave':
		# the client want to disconnect
		id = msg['id']
		del clients[id]
		print 'client #%s leave this server' % (id)
	elif cmd == 'sync':
		id = msg['id']
		if field.isWaiting():
			waited += 1
		else:
			waited = 0
		if waited < 5:
			foods = [x.pos for x in field.foods]
			blocks = [x.pos for x in field.blocks]
			snakes = []
			for snake in field.snakes:
				snakes.append({'name':snake.name,
					'body':[x.pos for x in snake.body],
					'direction':snake.direction,
					'stat':snake.statistic})

			new_msg = {'cmd':'sync_info', 
				'size':field.size,
				'round':field.round,
				'foods':foods, 'blocks':blocks, 'snakes':snakes}
			if clients[id][0] in ghosts:
				new_msg['youlost'] = 1
			client.send(repr(new_msg))
			# print 'sync at round %d' % (field.round)
		else:
			new_msg = "{'cmd':'waiting'}"
			client.send(new_msg)
	elif cmd == 'response':
		round = msg['round']
		if round != field.round:
			# something wrong
			client.send("{'cmd': 'fail', 'reason':'round not match'}")
		else:
			id = msg['id']
			direction = msg['direction']
			name = clients[id][0]
			field.acceptCommand(name, direction)
			client.send(msg_success)
		
def main():
	global clients, id_gener
	# clients = {id:(name, client), ...}
	clients = {}
	id_gener = IDGener()
	field = Field(fSize)
	initField(field)
	server = startServer()
	splash = '-'*80 + '\nWelcome to SnakeAIC server!\n' + '-'*80
	print splash
	print 'name: ', server.getsockname()
	input = [server, sys.stdin]

	frame_rate = config.frame_rate

	quit = False
	tm = pygame.time.Clock()

	time_max = 1000/frame_rate
	while not quit:
		time_cost = 0
		all_responsed = False
		# while time_cost < time_max:
		while not quit and not all_responsed:
			tm.tick()
			# input_ready, output_ready, exceptready = select.select(input, [], [], time_max - time_cost)
			input_ready, output_ready, exceptready = select.select(input, [], [])
			for s in input_ready:
				if s == server:
					client, address = server.accept()
					input.append(client)
				elif s == sys.stdin:
					# recieve command from stdin, commands can be:
					#   start #   stop #   restart #   quit
					command = sys.stdin.readline().rstrip()
					if command in ['q', 'quit']:
						quit = True
					if command in ['r', 'restart']:
						print 'reset'
						clients = {}
						field.reset()
						initField(field)
				else:
					# handle a client socket
					data = s.recv(config.data_maxsize)
					if data:
						# recieved data, begin handle it
						try:
							# print 'recieved: ', data
							parseCommand(field, data, s)
						except:
							print 'Warning: this is not a valid message\n\t%s'%data
							raise
					else:
						# maybe connection lost
						s.close()
						input.remove(s)
			for s in field.snakes:
				if s.name not in field._commands:
					all_responsed = False
					break
			else:
				all_responsed = True
			time_cost += tm.tick()

		tm.tick()
		if not field.isWaiting():
			ghosts = field.loop()
		elif waited > config.max_waited:
			field.reset()
			initField(filed)
			clients = {}
			
		time_max = max(1000/frame_rate - tm.tick(), 50)

		tm.tick(frame_rate)
		# print 'FPS:',tm.get_fps()
	print 'Bye'
		
if __name__ == '__main__':
	# cProfile.run('main()')
	main()
