import pygame
import bz2
import itertools
import config
import sys
import select
import socket
import xmlrpclib
from random import randint
from field import Field
from snake import *
from baseobj import *

X, Y = 0, 1
fSize = config.field_size1 # the field size

waited = 0
# to store the name of dead players, if that client send quit, remove the name 
# from here
ghosts = set()


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
		client.send(msg_success)
		print 'player %s quited the game' % (name)
	elif cmd == 'leave':
		# the client want to disconnect
		id = msg['id']
		del clients[id]
		client.send(msg_success)
		print 'client #%s leave this server' % (id)
	elif cmd == 'sync':
		id = msg['id']
		new_msg = {}
		if clients[id][0] in ghosts:
			new_msg['youlost'] = 1
		new_msg['cmd'] = 'sync_info'
		new_msg['info'] = field.getSyncInfo()
		new_msg = str(new_msg)
		print 'sync len', len(new_msg)
		client.send(new_msg)
		# print 'sync at round %d' % (field.round)
	elif cmd == 'response':
		round = msg['round']
		if round != field.round:
			# something wrong
			client.send("{'cmd': 'fail', 'round':%d, 'reason':'round not match'}"%(field.round))
		else:
			id = msg['id']
			direction = msg['direction']
			name = clients[id][0]
			field.acceptCommand(name, direction)
			client.send(msg_success)
		

def info():
	print 'clients', clients
	print 'field.snakes', field.snakes
	print 'waited', waited
	print 'ghosts', ghosts
def main():
	global clients, id_gener, reseted, field, ghosts
	# clients = {id:(name, client), ...}
	clients = {}
	id_gener = IDGener()
	field = Field(fSize)
	reseted = True
	server = startServer()
	splash = '-'*80 + '\nWelcome to SnakeAIC server!\n' + '-'*80
	print splash
	print 'name: ', server.getsockname()
	input = [server, sys.stdin]

	frame_rate = config.frame_rate

	quit = False
	tm = pygame.time.Clock()
	tm_fps = pygame.time.Clock()
	tm_fps.tick()

	time_max = 1000/frame_rate
	all_responsed = False
	frame = 0
	while not quit:
		time_cost = 0
		all_responsed = False
		while time_cost < time_max:
		# while (not quit) and (not all_responsed):
			tm.tick()
			input_ready, output_ready, exceptready = select.select(input, [], [], float(time_max - time_cost)/1000)
			# input_ready, output_ready, exceptready = select.select(input, [], [], 1)
			# print 'input_ready',input_ready
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
					if command in ['l', 'list']:
						info()
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
			# refresh all_responsed
			all_responsed = True
			for name, client in clients.itervalues():
				if name != None and (name not in field._commands):
					all_responsed = False
					break
			time_cost += tm.tick()

		# loop the game
		tm.tick()
		if field.started:
			new_ghosts = field.loop()
			names = [x[0] for x in clients.itervalues()]
			for g in new_ghosts:
				if g in names:
					ghosts.add(g)
			
		time_max = max(1000/frame_rate - tm.tick(), 50)

		tm_fps.tick(frame_rate)
		# frame += 1
		# if frame % 50 == 0:
		# 	print 'FPS:',tm_fps.get_fps()
	print 'Bye'
		
if __name__ == '__main__':
	# cProfile.run('main()')
	main()
