import random
import pygame
import time
import sys
import copy
from OpenGL.GL import *
from ctypes import *
from pygame.locals import *
from OpenGL.GLU import *
from pygit2 import Repository
from pygit2 import GIT_SORT_NONE

repostr = sys.argv[1] + "/.git"
repo = Repository(repostr)
vertices = []
colors = []

color_mergelines = [0.7, 0.7, 0.7]
color_commitlines = [0.50, 0.50, 0.80]

count = 0
x = 0
y = 2
z = 0

def drawText(font, mystr, x, y, z):
	tsf = font.render(mystr, True, (255, 255, 255, 0), (0, 0, 0, 255))
	fts = pygame.image.tostring(tsf, "RGBA", True)
	glRasterPos3d(*(x, y, z))
	glDrawPixels(tsf.get_width(), tsf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, fts)

pygame.init ()
display = (1280, 1024)
pygame.display.set_mode (display, pygame.OPENGL|pygame.DOUBLEBUF)
glClearColor (0.0, 0.0, 0.0, 1.0)
glEnableClientState (GL_VERTEX_ARRAY)
glEnableClientState (GL_COLOR_ARRAY)	
gluPerspective(45, (display[0]/display[1]), 0.1, 550.0)
glTranslatef(0.0, 0.0, -5)
selfont = pygame.font.match_font('ubuntucondensed')
font = pygame.font.Font(selfont, 18)

textlist = glGenLists(1)
glNewList (textlist, GL_COMPILE)
commit = repo.revparse_single('HEAD')
repohead = commit
random.seed(repohead.hex)

clen=0.07
nextlen = 5.00
visitedcommits = {'XXXX': 0}

class viscommit:
	def __init__(self, commitobj, x, y, z, px, py, pz):
		self.commitobj = commitobj
		self.parentx = px
		self.parenty = py
		self.parentz = pz
		self.x = x
		self.y = y
		self.z = z

def add_commit(colors, vertices, x, y, z, commit, clen, rendertext):
	colors.extend(color_mergelines)
	colors.extend(color_mergelines)
	colors.extend(color_mergelines)
	colors.extend(color_mergelines)
	colors.extend(color_mergelines)
	colors.extend(color_mergelines)
	colors.extend(color_mergelines)
	colors.extend(color_mergelines)

	# Draw commit symbol
	vertices.extend([x - clen/2, y, z])
	vertices.extend([x + clen/2, y, z])
	vertices.extend([x - clen/2, y - clen, z])
	vertices.extend([x + clen/2, y - clen, z])
	vertices.extend([x - clen/2, y, z])
	vertices.extend([x - clen/2, y - clen, z])
	vertices.extend([x + clen/2, y, z])
	vertices.extend([x + clen/2, y - clen, z])

	text = commit.hex[0:7] + " "  +  commit.message.split("\n")[0][0:10]
	if commit.hex in repohead.hex:
		text = text + "[HEAD] "
	if rendertext == True:
		drawText(font, text, x + 0.02, y + 0.03, z)

	if len(commit.parents) == 0:
		return colors, vertices


	colors.extend([0.50, 0.50, 0.80])
	colors.extend([0.50, 0.50, 0.80])
	vertices.extend([x, y - clen, z])
	vertices.extend([x, y - nextlen, z])
	if commit.parents[0].hex in visitedcommits:
		drawText(font, commit.parents[0].hex[0:7], x + 0.02, y - clen - nextlen, z)
	return colors, vertices

v = viscommit(commit, x, y, z, x, y, z)
orighead = copy.copy(v)
mergestack = [v]

pxs = x
switch = 0
xlim = 6.5
xlimextend = 6.5


commitscount = 1

starttime = int(round(time.time())) - 1

def printprogress(commitscount):
	curtime = int(round(time.time()))
	if commitscount % 25 == 0:
		print "total: ", commitscount, "commits per second: ", commitscount/(curtime - starttime)

while len(mergestack) > 0:
	vc = mergestack.pop()
	commit = vc.commitobj
	#print commit.hex, commit.message.split("\n")[0]
	x = float(vc.x)
	y = float(vc.y)
	z = float(vc.z)
	
	colors.extend(color_mergelines)
	colors.extend(color_mergelines)
	vertices.extend([x - clen/2, y - clen/2, z])
	vertices.extend([vc.parentx + clen/2, vc.parenty - clen/2, vc.parentz])
	colors, vertices = add_commit(colors, vertices, x, y, z, commit, clen, True)
	#if commit.hex in visitedcommits:
	#	continue
	visitedcommits[commit.hex] = 1
	printprogress(commitscount)
	commitscount = commitscount + 1
	while len(commit.parents) > 0:
		r = random.uniform(5, 10)
		if switch == 1:
			pxs = x + xlim + r
		else:
			pxs = x - xlim - r
		if len(commit.parents) > 1:
			for i, parent in enumerate(commit.parents):
				if i == 0:
					continue
				vc = viscommit(parent, pxs, y, z, x, y, z)
				if switch == 1:
					pxs = pxs + xlimextend
				else:
					pxs = pxs - xlimextend
				mergestack.append(vc)
			switch = 1 - switch
			xlim = xlim + xlimextend
			if xlim >= 5.0:
				xlim = xlimextend
		y = y - (nextlen)

		commit = commit.parents[0]
		if commit.hex in visitedcommits:
			break
		#print commit.hex,commit.message.split("\n")[0]
		colors, vertices = add_commit(colors, vertices, x, y, z, commit, clen, False)
		visitedcommits[commit.hex] = 1
		printprogress(commitscount)
		commitscount = commitscount + 1

		
glEndList ()
glShadeModel (GL_FLAT)

# create vertex buffer object
vbo = glGenBuffers (1)
glBindBuffer (GL_ARRAY_BUFFER, vbo)
glBufferData (GL_ARRAY_BUFFER, len(vertices)*4, (c_float*len(vertices))(*vertices), GL_STATIC_DRAW)
glVertexPointer (3, GL_FLOAT, 0, None)

# create color buffer object
cbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, cbo)
glBufferData(GL_ARRAY_BUFFER, len(colors)*4, (c_float*len(colors))(*colors), GL_STATIC_DRAW)
glColorPointer(3, GL_FLOAT, 0, None)

speed = 0.50
running = True
drawall = True
textrendering = False

glShadeModel (GL_FLAT)
pygame.key.set_repeat(2,10)

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
			break
		elif event.type == pygame.KEYDOWN:
			drawall = True
		elif event.type == pygame.KEYUP:
			drawall = True
			if event.key == pygame.K_t:
				textrendering = not textrendering
		kp = pygame.key.get_pressed()
		if kp[K_RIGHT] or kp[K_d]:
 			glTranslatef(-1 * speed, 0, 0)
 		elif kp[K_LEFT] or kp[K_a]:
			glTranslatef(speed, 0, 0)
		elif kp[K_w]:
			glTranslatef(0, 0,  speed)
		elif kp[K_s]:
			glTranslatef(0, 0, -1 * speed)
		elif kp[K_DOWN]:
			glTranslatef(0, speed,  0)
		elif kp[K_UP]:
			glTranslatef(0, -1 * speed, 0)
		elif kp[K_PAGEDOWN]:
			glTranslatef(0, speed * 10,  0)
		elif kp[K_PAGEUP]:
			glTranslatef(0, -1 * (speed * 10), 0)
		elif kp[K_z]:
			running = False
			break

	if drawall == True:
		# clear and draw everything!
		glClear (GL_COLOR_BUFFER_BIT)
		if textrendering == True:
			glCallList (textlist)
		# create vertex buffer object
		glDrawArrays (GL_LINES, 0, len(vertices)/3)
		pygame.display.flip ()
		drawall = False
	pygame.time.wait(10)
