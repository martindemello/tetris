#!/usr/bin/python

import exceptions
import pyglet
from pyglet.gl import *
from pyglet.window import key
import random

def bounds_check(fn): 
  def check(self, top, left, *args):
    if top < 0 or top > self.h or left < 1 or left > self.w:
      raise GridError("co-ordinates are not within %s, %s : %s, %s" % (self.h, self.w, top, left))
    return fn(self, top, left, *args)
  return check

class GridError(exceptions.Exception):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)

class Board():
  def __init__(self, height, width):
    self.h = height
    self.w = width
    self.cells = []
    self.anchor = None
    self.overlay = None
    self.color = None

  @bounds_check
  def on(self, top, left):
    for cell in self.cells:
      x, y, color = cell
      if x == top and y == left:
        return True
    return False

  @bounds_check
  def find(self, top, left):
    for index, cell in enumerate(self.cells):
      x, y, color = cell
      if x == top and y == left:
        return index
    return False

  @bounds_check
  def set(self, top, left, color=None):
    if self.color:
      color = self.color
    if not self.on(top, left):
      return self.cells.append((top, left, color))
  
  @bounds_check
  def unset(self, top, left):
    index = self.find(top, left)
    if not index == False:
      self.cells.remove(index)
      return True
 
  def collides(self, top, left):
    try:
      for c in self.overlay_cells_at(top, left, self.overlay.cells):
        x, y = c
        if self.on(x, y):
          return True
      return False
    except GridError:
      return True
      
  def transform(self, action):
    top, left = self.overlay.anchor
    new_top, new_left = None, None
    if action == 'left':
      new_top, new_left = top, left - 1
    if action == 'right':
      new_top, new_left = top, left + 1
    if action == 'up':
      new_top, new_left = top - 1, left
    if action == 'down':
      new_top, new_left = top + 1, left
      
    if self.collides(new_top, new_left):
      print "%s collides, cancelled" % action
    else:
      self.overlay.anchor = new_top, new_left
      
  def overlay_cells_at(self, top, left, cells):
    for c in cells:
      t, l, color = c
      new_top, new_left = top + t, left + l
      if not self.within_board(new_top, new_left):
        raise GridError('Not in grid!')
      yield (new_top, new_left)

  def overlay_cells(self):
    if self.overlay:
      for c in self.overlay.cells:
        top, left, color = c
        anchor_top, anchor_left = self.overlay.anchor
        new_top, new_left = top + anchor_top, left + anchor_left
        yield (new_top, new_left, color)
        
  def all(self):
    for c in self.cells:
      yield c
    for c in self.overlay_cells():
      yield c

  def within_board(self, top, left):
    return not top < 1 or top > self.h or left < 1 or left > self.w

class Tetromino(Board):
  def __init__(self, type=None):
    Board.__init__(self, 4, 4)
    self.color = (1, 0, 0)

  def set_many(self, *cells):
    for c in cells:
      x, y = c
      self.set(x, y)
      
  # piece names from http://en.wikipedia.org/wiki/Tetromino
  def stick(self): self.set_many((1, 1), (1, 2), (1, 3), (1, 4))
  def gamma(self): self.set_many((1, 1), (1, 2), (1, 3), (2, 1))
  def gun(self): self.set_many((2, 1), (2, 2), (2, 3), (3, 3))
  def square(self): self.set_many((1, 1), (1, 2), (2, 1), (2, 2))
  def enn(self): self.set_many((1, 1), (2, 1), (2, 2), (3, 2))
  def snake(self): self.set_many((1, 2), (2, 2), (2, 1), (3, 1))
  def tee(self): self.set_many((1, 2), (2, 1), (2, 2), (2, 3))

class BoardView(pyglet.window.Window):
  def __init__(self, width, height):
    pyglet.window.Window.__init__(self, width * 32, height * 32)
    self.rows = height
    self.columns = width
    self.init_game()

  def on_draw(self):
    glLoadIdentity()
    glShadeModel(GL_FLAT)
    glClear(GL_COLOR_BUFFER_BIT)
    self.draw_board()
    glFlush()

  def test_pattern(self):
    for row in range(self.rows + 1):
      for column in range(self.columns):
        color = random.random(), random.random(), random.random()
        self.draw_cell(row, column, color)

  def init_game(self):
    self.board = Board(self.rows, self.columns)
    self.board.set(1, 1, (1, 0, 0))
    self.board.set(1, 2, (1, 0.5, 0.6))
    self.board.set(8, 4, (0, 0, 1.0))
    self.board.set(self.rows, self.columns)

    self.board.overlay = Tetromino()
    self.board.overlay.square()
    self.board.overlay.anchor = (5, 5)

  def draw_board(self):
    for c in self.board.all():
      x, y, color = c
      self.draw_cell(x, y, color)

  def game_loop(self):
    pass
     
  def draw_cell(self, row, col, color=None):
    if not color: 
      r, g, b = 1, 1, 1
    else:
      r, g, b = color

    col = col - 1

    glBegin(GL_QUADS)
    glColor3f(r, g, b)
    bsize = 32
    margin = 2
    x0, y0 = col * bsize, self.height - row * bsize 
    x1, y1 = x0 + margin , y0 + margin
    x2, y2 = x0 + bsize - margin, y0 + margin
    x3, y3 = x0 + bsize - margin, y0 + bsize - margin
    x4, y4 = x0 + margin, y0 + bsize - margin
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glVertex2f(x4, y4)
    glEnd()

  def on_key_press(self, symbol, modifiers):
    if symbol == key.LEFT:
      self.board.transform('left')
    if symbol == key.RIGHT:
      self.board.transform('right')
    if symbol == key.UP:
      self.board.transform('up')
    if symbol == key.DOWN:
      self.board.transform('down')

if __name__ == '__main__':
  b = BoardView(10, 15)

  try:
    pyglet.app.run()
  except KeyboardInterrupt:
    pass
  
