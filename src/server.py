import pygame
import bz2
import itertools
import config
import sys
import select
import socket
from random import randint
from field import Field
from snake import *
from baseobj import *
from field_server import FieldServer

X, Y = 0, 1
fSize = config.field_size1 # the field size

def info():
	print 'clients', server.clients
	print 'field.snakes', field.snakes

def main():
	global field, server
	field = Field(fSize)
	server = FieldServer(("", config.server_port), field)

	splash = '-'*80 + '\nWelcome to SnakeAIC server!\n' + '-'*80
	print splash
	print 'name: ', server.socket.getsockname()

	frame_rate = config.frame_rate

	quit = False
	tm = pygame.time.Clock()
	tm_fps = pygame.time.Clock()
	tm_fps.tick()

	time_max = 1000/frame_rate
	all_responsed = False
	frame = 0
	while not quit:
		# all_responsed = False
		time_cost = 0
		cnt = 0
		while time_cost < time_max:
			server.serve(time_max - time_cost)
			cnt += 1
			time_cost += tm.tick()
		# recieve command from stdin, commands can be:
		#   start #   stop #   restart #   quit
		inputready = select.select([sys.stdin], [], [], 0.010)[0]
		if inputready:
			command = sys.stdin.readline().rstrip()
			if command in ['q', 'quit']:
				quit = True
			if command in ['r', 'restart']:
				print 'reset'
				clients = {}
				field.reset()
			if command in ['l', 'list']:
				info()
		# refresh all_responsed
		# all_responsed = True
		# for name, client in clients.itervalues():
		# 	if name != None and (name not in field._commands):
		# 		all_responsed = False
		# 		break

		# loop the game
		tm.tick()
		if field.started:
			field.loop()

		time_max = max(1000/frame_rate - tm.tick(), 50)

		tm_fps.tick(frame_rate)
		# frame += 1
		# if frame % 50 == 0:
		# 	print 'FPS:',tm_fps.get_fps()
	print 'Bye'

if __name__ == '__main__':
	# cProfile.run('main()')
	main()
