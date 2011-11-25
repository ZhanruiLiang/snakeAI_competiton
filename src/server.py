import pygame
import itertools
import config
import sys
import select
from random import randint
from field import Field
from baseobj import *

X, Y = 0, 1

def initField(field):
	fSize = config.field_size1 # the field size

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
	server.bind(('', config.server_port))
	server.listen(config.server_backlog)
	return server
		
def main():
	field = Field(fSize)
	initField(field)
	server = startServer()
	input = [server, sys.stdin]

	frame_rate = config.frame_rate

	quit = False
	tm = pygame.time.Clock()

	while not quit:
		tm.tick()
		field.loop()
		time_max = max(100 - tm.tick(), 50)
		time_cost = 0
		while time_cost < time_max:
			tm.tick()
			input_ready, output_ready, exceptready = select.select(input, [], [], time_max - time_cost)
			for s in input_ready:
				if s == server:
					client, address = server.accept()
					input.append(client)
				elif s == sys.stdin:
					# recieve command from stdin, commands can be:
					#   start #   stop #   restart #   quit
					command = sys.stdin.readline().rstrip()
					if command == 'quit':
						quit = True
				else:
					# handle a client socket
					data = s.recv(config.data_maxsize)
					if data:
						# recieved data, begin handle it
						# TODO
						pass
					else:
						# maybe connection lost
						s.close()
						input.remove(s)
			time_cost += tm.tick()

		tm.tick(frame_rate)
		# print 'FPS:',tm.get_fps()
	
	print 'Bye'
		
if __name__ == '__main__':
	# cProfile.run('main()')
	main()
