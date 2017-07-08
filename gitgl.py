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
color_mergelines =  [0.05, 0.05, 0.45]
color_commitlines = [0.10, 0.10, 0.40]
color_commitbox = [0.93, 0.93, 0.93]
count = 0
x = 0
y = 2
z = 0
clen = 0.90
nextlen = 5.00
visitedcommits = {'XXXX': 0}

textcolor = (190, 190, 190, 0)
imptextcolor = (255, 255, 255, 0)

def drawText(font, mystr, x, y, z, forecolor):
	tsf = font.render(mystr, True, forecolor, (0, 0, 0, 255))
	fts = pygame.image.tostring(tsf, "RGBA", True)
	glRasterPos3d(*(x, y, z))
	glDrawPixels(tsf.get_width(), tsf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, fts)

pygame.init ()
display = (1280, 1024)
pygame.display.set_mode (display, pygame.OPENGL|pygame.DOUBLEBUF)
glClearColor (0.0, 0.0, 0.0, 1.0)
glEnableClientState (GL_VERTEX_ARRAY)
glEnableClientState (GL_COLOR_ARRAY)	
gluPerspective(45, (display[0]/display[1]), 0.01, 9250.0)
glTranslatef(0.0, 0.0, -50)
selfont = pygame.font.match_font('ubuntucondensed')
font = pygame.font.Font(selfont, 18)
commit = repo.revparse_single(sys.argv[2])
impcommithash = sys.argv[3]
impcommit = repo.revparse_single(impcommithash)
repohead = commit
random.seed(repohead.hex)

class viscommit:
	def __init__(self, commitobj, childcommitobj, x, y, z, px, py, pz, mergecolor, switch):
		self.commitobj = commitobj
		self.childcommit = childcommitobj
		self.parentx = px
		self.parenty = py
		self.parentz = pz
		self.x = x
		self.y = y
		self.z = z
		self.mergecolor = mergecolor
		self.switch = switch

def add_commit(colors, vertices, x, y, z, commit, clen, rendertext, commitlinescolor):
	colors.extend(color_commitbox)
	colors.extend(color_commitbox)
	colors.extend(color_commitbox)
	colors.extend(color_commitbox)
	colors.extend(color_commitbox)
	colors.extend(color_commitbox)
	colors.extend(color_commitbox)
	colors.extend(color_commitbox)

	# Draw commit symbol
	vertices.extend([x - clen/2, y, z])
	vertices.extend([x + clen/2, y, z])
	vertices.extend([x - clen/2, y - clen, z])
	vertices.extend([x + clen/2, y - clen, z])
	vertices.extend([x - clen/2, y, z])
	vertices.extend([x - clen/2, y - clen, z])
	vertices.extend([x + clen/2, y, z])
	vertices.extend([x + clen/2, y - clen, z])

	text = commit.hex[0:8] + " "  +  commit.message.split("\n")[0][0:80]
	if commit.hex in repohead.hex:
		text = text + "[HEAD] "
	elif rendertext == True:
		drawText(font, text, x + 0.02, y + 0.03, z, textcolor)

	if len(commit.parents) == 0:
		return colors, vertices, 0

	randy = random.uniform(25, 50)
	colors.extend(commitlinescolor)
	colors.extend(commitlinescolor)
	vertices.extend([x, y - clen, z])
	vertices.extend([x, y - nextlen - randy, z])
	if commit.parents[0].hex in visitedcommits:
		drawText(font, commit.parents[0].hex[0:8], x + 0.02, y - clen - nextlen - randy, z, textcolor)
	return colors, vertices, randy

v = viscommit(commit, None, x, y, z, x, y, z, color_commitlines, 0)
orighead = copy.copy(v).commitobj
mergestack = [v]
pxs = x
switch = 0
xlim = 20
xlimextend = 20
commitscount = 1
starttime = int(round(time.time())) - 1

def printprogress(commitscount):
	curtime = int(round(time.time()))
	if commitscount % 7000 == 0:
		print "total: ", commitscount, "commits per second: ", commitscount/(curtime - starttime)

centrallinecolor = [0.7, 0.2, 0.2]
firstline = True

textlist = glGenLists(1)
glNewList (textlist, GL_COMPILE)
while len(mergestack) > 0:
	vc = mergestack.pop()
	commit = vc.commitobj
	#print commit.hex, commit.message.split("\n")[0]
	x = float(vc.x)
	y = float(vc.y)
	z = float(vc.z)
	colors.extend(vc.mergecolor)
	colors.extend(vc.mergecolor)
	colors.extend(vc.mergecolor)
	colors.extend(vc.mergecolor)
	vertices.extend([x, y - clen/2, z])
	vertices.extend([x, vc.parenty - clen/2, vc.parentz])
	vertices.extend([x, vc.parenty - clen/2, vc.parentz])
	vertices.extend([vc.parentx, vc.parenty - clen/2, vc.parentz])
	color_commitlines[2] = (float(125) + random.uniform(126, 205)) / 255

	# if we've seen this before, draw the commit text and continue on to the next merge
	if commit.hex in visitedcommits and commit.hex not in orighead.hex:
		drawText(font, commit.parents[0].hex[0:8], x + 0.02, y - clen - nextlen - randy, z, textcolor)
		continue
	if firstline == True:
		commitlinescolor = centrallinecolor
	else:
		commitlinescolor = color_commitlines
	colors, vertices, randy = add_commit(colors, vertices, x, y, z, commit, clen, True, commitlinescolor)
	if impcommit.hex in commit.hex:
		visitedcommits[commit.hex] = (x, y, z, commit, vc.childcommit, firstline)
	else:
		visitedcommits[commit.hex] = (x, y, z, commit, vc.childcommit, firstline)
	printprogress(commitscount)
	commitscount = commitscount + 1
	while len(commit.parents) > 0:
		r = random.uniform(5, 10)
		if firstline:
			sw = switch
			switch = 1 - switch
		else:
			sw = vc.switch
		if sw == 1:
			pxs = x + xlim * r
		else:
			pxs = x - (xlim * r)
		ismerge = False
		if len(commit.parents) > 1:
			ismerge = True
			vcmergecolor = copy.copy(color_mergelines)
			vcmergecolor[2] = (float(40) + random.uniform(41, 205)) / 255
			for i, parent in enumerate(commit.parents):
				r = random.uniform(5, 10)
				q = random.uniform(25, 50)
				if i == 0:
					continue
				if sw == 1:
					pxs = pxs + xlimextend * r
				else:
					pxs = pxs - (xlimextend * r)
				pxy = y - q
				vc = viscommit(parent, commit, pxs, pxy, z, x, y, z, vcmergecolor, sw)
				mergestack.append(vc)
			xlim = xlim + xlimextend
			if xlim >= 5.0:
				xlim = xlimextend
		y = y - (nextlen) - randy

		childcommit = commit
		commit = commit.parents[0]
		#print commit.hex,commit.message.split("\n")[0]
		if commit.hex in visitedcommits:
			break
		(colors, vertices, randy) = add_commit(colors, vertices, x, y, z, commit, clen,
							ismerge or (len(commit.parents) > 1),
							commitlinescolor)
		if impcommit.hex in commit.hex:
			visitedcommits[commit.hex] = (x, y, z, commit, childcommit, firstline)
		else:
			visitedcommits[commit.hex] = (x, y, z, commit, childcommit, firstline)
		printprogress(commitscount)
		commitscount = commitscount + 1

	if firstline == True:
		(colors, vertices, randy) = add_commit(colors, vertices, x, y, z, commit, clen,
							True,
							commitlinescolor)
	firstline = False

implinescolor = [1, 1, 1]
print "Starting highlight procedure..."
traverse = visitedcommits[impcommit.hex]
while traverse[5] is not True:
	x = traverse[0]
	y = traverse[1]
	z = traverse[2]
	child = visitedcommits[traverse[4].hex]
	if child is None:
		break

	cx = child[0]
	cy = child[1]
	cz = child[2]

	if x == cx:
		colors.extend(implinescolor)
		colors.extend(implinescolor)
		vertices.extend([x, y, z])
		vertices.extend([cx, cy, cz])
	else:
		# reached a merge point!
		colors.extend(implinescolor)
		colors.extend(implinescolor)
		colors.extend(implinescolor)
		colors.extend(implinescolor)
		vertices.extend([x, y, z])
		vertices.extend([x, cy - clen/2, z])
		vertices.extend([x, cy - clen/2, z])
		vertices.extend([cx, cy - clen/2, z])
	traverse = visitedcommits[traverse[4].hex]
print "Finished highlight procedure..."

glEndList ()
glShadeModel (GL_FLAT)
print "Finished constructing text lists"


def highlight_commit(hcommit):
	hvertices = []
	hcolors = []
	traverse = visitedcommits[hcommit.hex]
	hx = traverse[0]
	hy = traverse[1]
	hz = traverse[2]
	htextlist = glGenLists(1)
	glNewList (htextlist, GL_COMPILE)
	drawText(font, hcommit.message.split("\n")[0], hx + 0.02, hy + 0.03, hz, imptextcolor)

	while traverse[5] is not True:
		x = traverse[0]
		y = traverse[1]
		z = traverse[2]
		child = visitedcommits[traverse[4].hex]
		if child is None:
			break

		cx = child[0]
		cy = child[1]
		cz = child[2]

		if x != cx:
			msg = child[3].hex[0:8] + " " + child[3].message.split("\n")[0][0:51]
			drawText(font, msg, cx + clen/2 + 0.05, cy + clen/2 + 0.05, cz, imptextcolor)

		if x == cx:
			hcolors.extend(implinescolor)
			hcolors.extend(implinescolor)
			hvertices.extend([x, y, z])
			hvertices.extend([cx, cy, cz])
		else:
			# reached a merge point!
			hcolors.extend(implinescolor)
			hcolors.extend(implinescolor)
			hcolors.extend(implinescolor)
			hcolors.extend(implinescolor)
			hvertices.extend([x, y, z])
			hvertices.extend([x, cy - clen/2, z])
			hvertices.extend([x, cy - clen/2, z])
			hvertices.extend([cx, cy - clen/2, z])
		traverse = visitedcommits[traverse[4].hex]
	glEndList ()
	glShadeModel (GL_FLAT)

	hbo = glGenBuffers (1)
	glBindBuffer (GL_ARRAY_BUFFER, hbo)
	glBufferData (GL_ARRAY_BUFFER, len(hvertices)*4, (c_float*len(hvertices))(*hvertices), GL_STATIC_DRAW)
	glVertexPointer (3, GL_FLOAT, 0, None)

	hcbo = glGenBuffers(1)
	glBindBuffer(GL_ARRAY_BUFFER, hcbo)
	glBufferData(GL_ARRAY_BUFFER, len(hcolors)*4, (c_float*len(hcolors))(*hcolors), GL_STATIC_DRAW)
	glColorPointer(3, GL_FLOAT, 0, None)

	return hvertices, hbo, hcbo, htextlist, hx, hy, hz
		

print "Binding buffers..."
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
print "....done. Number of vertices:", len(vertices)

speed = 32.0
running = True
drawall = True
textrendering = False

glShadeModel (GL_FLAT)
pygame.key.set_repeat(2,10)

impx = visitedcommits[impcommit.hex][0]
impy = visitedcommits[impcommit.hex][1]
impz = visitedcommits[impcommit.hex][2]
importantcommit = visitedcommits[impcommit.hex][3]

lookdistance = 250
gluLookAt(impx, impy, lookdistance, impx, impy, 0, 0, 1, 0)

hbo = 0
hcbo = 0
htextlist = 0
hvertices = []
overx = -40
overy = 40
overz = 200

startcommitsearch = False

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
			elif event.key == pygame.K_q:
				speed *= 2
				if speed > 1024:
					speed = 1024
				print speed
			elif event.key == pygame.K_r:
				speed /= 2
				if speed <= 1:
					speed = 1
				print speed
			elif event.key == pygame.K_SLASH:
				startcommitsearch = True
				searchhex = ""
			elif event.key == pygame.K_ESCAPE:
				startcommitsearch = False
				searchhex = ""
			elif startcommitsearch and event.key >= pygame.K_a and event.key <= pygame.K_z:
				n = ord('a') + (event.key - pygame.K_a)
				if pygame.key.get_mods() & (KMOD_SHIFT | KMOD_CAPS):
					n = ord('A') + (event.key - pygame.K_a)
				searchhex += chr(n)
				print searchhex
			elif startcommitsearch and event.key >= pygame.K_a and event.key <= pygame.K_f:
				n = 10 + event.key - pygame.K_a
				searchhex += str(hex(n)).replace("0x", "")
				print searchhex
			elif startcommitsearch and event.key >= pygame.K_0 and event.key <= pygame.K_9:
				n = event.key - pygame.K_0
				searchhex += str(n)
				print searchhex
			elif startcommitsearch and event.key == K_BACKSPACE:
				if len(searchhex) > 0:
					searchhex = searchhex[0:len(searchhex)-1]

		if startcommitsearch and len(searchhex) > 7:
			try:
				hcommit = repo.revparse_single(searchhex)
			except:
				print "Couldn't find " + searchhex
				startcommitsearch = False
				continue
			startcommitsearch = False
			hvertices, hbo, hcbo, htextlist, hx, hy, hz = highlight_commit(hcommit)
			drawall = True
			glLoadIdentity()
			gluPerspective(45, (display[0]/display[1]), 0.01, 9250.0)
			gluLookAt(hx, hy, lookdistance, hx, hy, 0, 0, 1, 0)
			overx = hx - 10
			overy = hy + 10
			overz = 200

		kp = pygame.key.get_pressed()
		if kp[K_RIGHT]:
 			glTranslatef(-1 * speed, 0, 0)
			overx += speed
 		if kp[K_LEFT]:
			glTranslatef(speed, 0, 0)
			overx -= speed
		if kp[K_w]:
			glTranslatef(0, 0,  speed)
			overz -= speed
		if kp[K_s]:
			glTranslatef(0, 0, -1 * speed)
			overz += speed
		if kp[K_DOWN]:
			glTranslatef(0, speed,  0)
			overy -= speed
		if kp[K_UP]:
			glTranslatef(0, -1 * speed, 0)
			overy += speed
		if kp[K_z]:
			running = False
			break

	if drawall == True:
		# clear and draw everything!
		glClear (GL_COLOR_BUFFER_BIT)
		if textrendering == True:
			glCallList (textlist)
		msg = importantcommit.hex[0:8] + " " + importantcommit.message.split("\n")[0][0:51]
		drawText(font, msg, impx + clen/2 + 0.05, impy + clen/2 + 0.05, impz, imptextcolor)
		glBindBuffer (GL_ARRAY_BUFFER, vbo)
		glVertexPointer (3, GL_FLOAT, 0, None)
		glBindBuffer (GL_ARRAY_BUFFER, cbo)
		glColorPointer (3, GL_FLOAT, 0, None)
		# create vertex buffer object
		glDrawArrays (GL_LINES, 0, len(vertices)/3)
		drawText(font, "gitGL", overx, overy, overz, imptextcolor)
		if startcommitsearch:
			drawText(font, "search:  " + searchhex, overx, overy - 2, overz, imptextcolor)
		drawText(font, "speed:  " + str(speed), overx, overy - 3.5, overz, imptextcolor)

		if hbo > 0:
			pxpe = 1
			glBindBuffer (GL_ARRAY_BUFFER, hbo)
			glVertexPointer (3, GL_FLOAT, 0, None)
			glBindBuffer(GL_ARRAY_BUFFER, hcbo)
			glColorPointer(3, GL_FLOAT, 0, None)
			glLineWidth(2)	
			glDrawArrays (GL_LINES, 0, len(hvertices)/3)
			glLineWidth(1)	
			glCallList (htextlist)
		pygame.display.flip ()
		drawall = False
	pygame.time.wait(10)
