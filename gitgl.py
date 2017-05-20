import pygame
import sys
import copy
from OpenGL.GL import *
from ctypes import *
from pygame.locals import *
from OpenGL.GLU import *
from pygit2 import Repository
from pygit2 import GIT_SORT_NONE

repostr = sys.argv[1]+"/.git"
repo = Repository(repostr)
vertices = []
colors = []

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
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -5)
selfont = pygame.font.match_font('ubuntucondensed')
font = pygame.font.Font(selfont, 16)

textlist = glGenLists(1)
glNewList (textlist, GL_COMPILE)
commit = repo.revparse_single('HEAD')
repohead = commit

clen=0.03
coffset = 0.02
nextlen = 0.48

class viscommit:
	def __init__(self, commitobj, mergebase, x, y, z, px, py, pz):
		self.commitobj = commitobj
		self.mergebase = mergebase
		self.parentx = px
		self.parenty = py
		self.parentz = pz
		self.x = x
		self.y = y
		self.z = z

def add_commit(colors, vertices, x, y, z, commit, clen, mb):
	colors.extend([1, 0, 0])
	colors.extend([1, 0, 0])
	colors.extend([1, 0, 0])
	colors.extend([1, 0, 0])
	colors.extend([1, 0, 0])
	colors.extend([1, 0, 0])
	colors.extend([1, 0, 0])
	colors.extend([1, 0, 0])

	# Draw commit symbol
	vertices.extend([x - clen/2, y, z])
	vertices.extend([x + clen/2, y, z])
	vertices.extend([x - clen/2, y - clen, z])
	vertices.extend([x + clen/2, y - clen, z])
	vertices.extend([x - clen/2, y, z])
	vertices.extend([x - clen/2, y - clen, z])
	vertices.extend([x + clen/2, y, z])
	vertices.extend([x + clen/2, y - clen, z])

	text = commit.hex[0:7] + " "  +  commit.message.split("\n")[0][0:5]
	if commit.hex in repohead.hex:
		text = text + "[HEAD] "
	if mb is not None: # and len(commit.parents) > 0 and mb.hex == commit.parents[0].hex:
		text = text + "[mb: " + mb.hex[0:7] + "]"
	drawText(font, text, x + 0.01, y, z)

	if len(commit.parents) > 0:
		if mb is not None and mb.hex == commit.parents[0].hex:
			return colors, vertices

	if len(commit.parents) == 0:
		return colors, vertices

	colors.extend([0, 0, 1])
	colors.extend([0, 0, 1])
	vertices.extend([x, y - clen, z])
	vertices.extend([x, y - nextlen, z])
	return colors, vertices

v = viscommit(commit, None, x, y, z, x, y, z)
orighead = copy.copy(v)
mergestack = [v]

pxs = x
switch = 0
xlim = 2.5
xlimextend = 2.5

visitedcommits = {'XXXX': 0}

while len(mergestack) > 0:
	vc = mergestack.pop()
	commit = vc.commitobj
	print commit.hex, commit.message.split("\n")[0]
	x = float(vc.x)
	y = float(vc.y)
	z = float(vc.z)
	
	colors.extend([1, 0, 0])
	colors.extend([1, 0, 0])
	vertices.extend([x - clen/2, y - clen/2, z])
	vertices.extend([vc.parentx + clen/2, vc.parenty - clen/2, vc.parentz])
	mb = vc.mergebase
	colors, vertices = add_commit(colors, vertices, x, y, z, commit, clen, mb)
	#if commit.hex in visitedcommits:
	#	continue
	visitedcommits[commit.hex] = 1
	while len(commit.parents) > 0:
		if switch == 1:
			pxs = x + xlim
		else:
			pxs = x - xlim
		if len(commit.parents) > 1:
			for i, parent in enumerate(commit.parents):
				if i == 0:
					continue
				mergebase = repo.merge_base(commit.parents[0].hex, parent.hex)
				print "    mb:", mergebase.hex
				vc = viscommit(parent, mergebase, pxs, y, z, x, y, z)
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
		if mb is not None and mb.hex == commit.hex:
			break
		print commit.hex,commit.message.split("\n")[0]
		colors, vertices = add_commit(colors, vertices, x, y, z, commit, clen, mb)
		visitedcommits[commit.hex] = 1

		
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

speed = 0.20
running = True
drawall = True

glShadeModel (GL_FLAT)
pygame.key.set_repeat(2,10)

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
			break
		elif event.type == pygame.KEYDOWN:
			drawall = True

		kp = pygame.key.get_pressed()
		if kp[K_RIGHT] or kp[K_d]:
 			glTranslatef(-1 * speed, 0, 0)
 		elif kp[K_LEFT] or kp[K_a]:
			glTranslatef(speed, 0, 0)
		elif kp[K_w]:
			glTranslatef(0, 0,  speed)
		elif kp[K_s]:
			glTranslatef(0, 0, -1 * speed)
		elif kp[K_UP]:
			glTranslatef(0, speed,  0)
		elif kp[K_DOWN]:
			glTranslatef(0, -1 * speed, 0)
		elif kp[K_PAGEUP]:
			glTranslatef(0, speed * 10,  0)
		elif kp[K_PAGEDOWN]:
			glTranslatef(0, -1 * (speed * 10), 0)
		elif kp[K_z]:
			running = False
			break

	if drawall == True:
		# clear and draw everything!
		glClear (GL_COLOR_BUFFER_BIT)
		glCallList (textlist)
		# create vertex buffer object
		glDrawArrays (GL_LINES, 0, len(vertices)/3)
		pygame.display.flip ()
		drawall = False
	pygame.time.wait(10)
