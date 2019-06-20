import atexit
import curses
import curses.ascii
import time
from random import randint


class SnakeUI(object):
    """Handles all I/O"""

    def __init__(self, engine):
        self.engine = engine
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)

    def destroy(self):
        curses.endwin()

    def render(self):
        self.stdscr.erase()
        # FIXME there are off by ones
        for col in range(1, self.engine.width + 2):
            self.stdscr.addch(1, col, '-')
            self.stdscr.addch(self.engine.height, col, '-')
        for row in range(1, self.engine.height + 2):
            self.stdscr.addch(row, 1, '|')
            self.stdscr.addch(row, self.engine.width, '|')
        for x, y in self.engine.snake:
            self.stdscr.addch(y + 2, x + 2, 'X')
        x, y = self.engine.apple
        self.stdscr.addch(y + 2, x + 2, '@')
        self.stdscr.refresh()

    def process_inputs(self):
        player_shift = 0
        while True:
            ch = self.stdscr.getch()
            if ch == -1:  # no more inputs
                break
            elif ch == curses.KEY_UP:
                self.engine.change_direction(SnakeEngine.UP)
            elif ch == curses.KEY_DOWN:
                self.engine.change_direction(SnakeEngine.DOWN)
            elif ch == curses.KEY_LEFT:
                self.engine.change_direction(SnakeEngine.LEFT)
            elif ch == curses.KEY_RIGHT:
                self.engine.change_direction(SnakeEngine.RIGHT)
            elif ch == ord('q'):
                self.engine.quit()


class SnakeEngine(object):
    """Game state and logic"""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.running = True
        # front of list is head, back of list is tail
        self.snake = [(self.width // 2, self.height // 2)]
        self.direction = self.RIGHT
        self.spawn_apple()
        # TODO track score

    def spawn_apple(self):
        while True:
            self.apple = (randint(0, self.width - 1), randint(0, self.height - 1))
            if self.apple not in self.snake:
                break

    def quit(self):
        self.running = False

    def game_over(self):
        # TODO present game over screen
        self.running = False

    def change_direction(self, direction):
        self.direction = direction

    def tick(self):
        curr_head = self.snake[0]
        next_head = tuple(map(sum, zip(curr_head, self.direction)))

        # TODO grow by more than 1
        if next_head == self.apple:
            # TODO spawn should probably happen after next_head is pushed
            self.spawn_apple()
        else:
            # self.snake.pop() # in jmou's version, prevents snake from growing
            pass

        # Collision detect against snake body or game bounds. We do this after
        # shrinking the tail so you can Ouroboros.
        if (next_head in self.snake or next_head[0] < 0 or next_head[0] >
                self.width or next_head[1] < 0 or next_head[1] > self.height):
            self.game_over()

        self.snake = [next_head] + self.snake


if __name__ == '__main__':
    # TODO get dimensions from terminal
    engine = SnakeEngine(80, 24) # jmou's version has 80, 40
    ui = SnakeUI(engine)
    atexit.register(ui.destroy)
    ui.render()
    while engine.running:
        time.sleep(.1)
        ui.process_inputs()
        engine.tick()
        ui.render()
