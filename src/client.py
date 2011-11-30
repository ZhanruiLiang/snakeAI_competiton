"""
usage: client.py [-h host] [-p AI]
"""
import pygame
import config
from field_client import FieldClient
from render import Render
import sys
import socket

X, Y = 0, 1

def init():
	pygame.display.init()
	pygame.font.init()

def quitclean():
	pygame.display.quit()
	pygame.font.quit()

def parseOptions():
	# return (host, AI)
	argv = sys.argv
	i = 1
	host, AI = 'localhost', None
	while i < len(argv):
		opt = argv[i]
		if opt == '-h':
			host = argv[i+1]
			i += 1
		elif opt == '-p':
			AI = __import__(sys.argv[i+1])
			i += 1
		i += 1
	return host, AI

def main():
	init()

	host, AI = parseOptions()

	field = FieldClient()
	field.connect(host)
	if AI:
		snake = AI.SnakeAI(field)
		print 'join', AI
		field.join(snake)

	sSize = config.screen_size #the screen size
	fSize = config.field_size1 # the field size
	frame_rate = config.frame_rate

	screen = pygame.display.set_mode(sSize, 0, 32)
	pygame.display.set_caption('SnakeAIC')

	render = Render(field, screen)
	timer = pygame.time.Clock()
	quit = False
	while not quit:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit = True
		field.sync()

		render.render()
		# for debug
		# render.render_path(snake._path)
		# render.render_coor()
		#
		pygame.display.flip()
		timer.tick(frame_rate)
		# print timer.get_fps()

	field.disconnect()
	quitclean()
	print "Bye"
if __name__ == '__main__':
	main()
