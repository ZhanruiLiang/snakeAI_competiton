import pygame as pg
pg.display.init()
scr = pg.display.set_mode((400, 400))
img = pg.image.load('res/dashboard.png').convert()
size = img.get_size()

def func1():
	scr.blit(img, (20, 30))

def func2():
	pg.draw.rect(scr, (0, 32, 40), (20, 30, size[0], size[1]))

func = func2
for i in xrange(52500):
	func()

pg.display.flip()
pg.display.quit()

