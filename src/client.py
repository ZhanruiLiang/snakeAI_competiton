"""
usage: client.py ai_script [host]
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

def main():
	init()

	if len(sys.argv) >= 3:
		host = sys.argv[2]
	else:
		host = 'localhost'
	if len(sys.argv) >= 2:
		AI = __import__(sys.argv[1])
	else:
		AI = None

	field = FieldClient()
	field.connect(host)
	if AI:
		snake = AI.SnakeAI(field)
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
