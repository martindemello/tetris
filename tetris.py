#!/usr/bin/python

import exceptions
import pyglet
from pyglet.gl import *
from pyglet.window import key
import random

def bounds_check(fn): 
  def check(self, top, left):
    if top < 0 or top > self.h or left < 0 or left > self.w:
      raise GridError("co-ordinates are not within %s, %s : %s, %s" % (self.h, self.w, top, left))
    return fn(self, top, left)
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

  @bounds_check
  def on(self, top, left):
    for cell in self.cells + self.overlay_cells:
      x, y = cell
      if x == left and y == top:
        return True
    return False

  @bounds_check
  def find(self, top, left):
    for index, cell in enumerate(self.cells):
      x, y = cell
      if x == left and y == top:
        return index
    return False

  @bounds_check
  def set(self, top, left):
    if not self.on(top, left):
      return self.cells.append((top, left))
  
  @bounds_check
  def unset(self, top, left):
    index = self.find(top, left)
    if not index == False:
      self.cells.remove(index)
      return True

  def all(self):
    for c in self.cells + self.overlay_cells:
      yield c

  def overlay(self, top, left, board):
    self.overlay_pos = (top, left)
    self.overlay_board = board
    self.overlay_cells = []
    self.new_overlay_cells 
    for cell in self.overlay_board.cells:
      x, y = cell
      self.overlay_cells.append((x + top, y + left))

  def overlay_transform(self, direction):
    new_overlay = []
    top, left = self.overlay_pos 
    if direction == 'LEFT':
      self.overlay(top, left - 1, self.overlay_board)
    if direction == 'RIGHT':
      self.overlay(top, left + 1, self.overlay_board)
    if direction == 'DOWN':
      self.overlay(top + 1, left, self.overlay_board)
    if direction == 'UP':
      self.overlay(top - 1, left, self.overlay_board)
  
    
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
    self.board.set(1, 1)
    self.board.set(1, 2)
    self.board.set(2, 2)
    self.board.set(3, 3)

    ol = Board(2, 2)
    ol.set(1, 1)
    ol.set(2, 1)
    ol.set(2, 2)

    self.board.overlay(5, 5, ol)

  def draw_board(self):
    for c in self.board.all():
      x, y = c
      self.draw_cell(x, y)

  def game_loop(self):
    pass
     
  def draw_cell(self, row, col, color=None):
    if not color: 
      r, g, b = 1, 1, 1
    else:
      r, g, b = color
    
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
      self.board.overlay_transform('LEFT')
    if symbol == key.RIGHT:
      self.board.overlay_transform('RIGHT')
    if symbol == key.UP:
      self.board.overlay_transform('UP')
    if symbol == key.DOWN:
      self.board.overlay_transform('DOWN')

if __name__ == '__main__':
  b = BoardView(10, 15)

  try:
    pyglet.app.run()
  except KeyboardInterrupt:
    pass
  
