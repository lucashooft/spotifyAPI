"""Mini snake game for the terminal. Standard library only, no curses.

Run with: python snake.py
Controls: arrow keys or WASD to steer, p to pause, q to quit.

Works on Windows, macOS and Linux: input uses msvcrt or termios depending on
the platform, drawing uses plain ANSI escape codes.
"""

import os
import random
import shutil
import sys
import time

WIDTH = 30
HEIGHT = 18
START_LENGTH = 4
START_DELAY = 0.12     # seconds between steps
MIN_DELAY = 0.055
SPEEDUP = 0.004        # shaved off per apple

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

DIRECTIONS = {
    "up": UP, "w": UP,
    "down": DOWN, "s": DOWN,
    "left": LEFT, "a": LEFT,
    "right": RIGHT, "d": RIGHT,
}

HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
CLEAR = "\x1b[2J"
HOME = "\x1b[H"
GREEN = "\x1b[32m"
RED = "\x1b[31m"
RESET = "\x1b[0m"


# --- keyboard ---------------------------------------------------------------

if os.name == "nt":
    import msvcrt

    ARROWS = {"H": "up", "P": "down", "K": "left", "M": "right"}

    class KeyReader:
        """Non-blocking key reader for the Windows console."""

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            keys = []
            while msvcrt.kbhit():
                char = msvcrt.getwch()
                if char in ("\x00", "\xe0"):        # arrow key prefix
                    key = ARROWS.get(msvcrt.getwch())
                    if key:
                        keys.append(key)
                else:
                    keys.append(char.lower())
            return keys

else:
    import select
    import termios
    import tty

    ARROWS = {"[A": "up", "[B": "down", "[C": "left", "[D": "right"}

    class KeyReader:
        """Non-blocking key reader for a POSIX terminal."""

        def __enter__(self):
            self.fd = sys.stdin.fileno()
            self.saved = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
            return self

        def __exit__(self, *exc):
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.saved)
            return False

        def _pending(self):
            return bool(select.select([self.fd], [], [], 0)[0])

        def read(self):
            keys = []
            while self._pending():
                char = os.read(self.fd, 1).decode("utf-8", "ignore")
                if char == "\x1b":                  # escape sequence
                    seq = ""
                    while self._pending() and len(seq) < 2:
                        seq += os.read(self.fd, 1).decode("utf-8", "ignore")
                    key = ARROWS.get(seq)
                    keys.append(key if key else "q")
                elif char:
                    keys.append(char.lower())
            return keys


def enable_ansi():
    """Turn on escape sequence handling in older Windows consoles."""
    if os.name != "nt":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


# --- game -------------------------------------------------------------------

class Game:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        head = (WIDTH // 2, HEIGHT // 2)
        self.snake = [(head[0] - i, head[1]) for i in range(START_LENGTH)]
        self.direction = RIGHT
        self.pending = RIGHT
        self.score = 0
        self.delay = START_DELAY
        self.won = False
        self.apple = self.new_apple()

    def new_apple(self):
        taken = set(self.snake)
        free = [(x, y) for x in range(WIDTH) for y in range(HEIGHT) if (x, y) not in taken]
        return self.rng.choice(free) if free else None

    def turn(self, direction):
        # ignore a reversal straight into the neck
        if (direction[0] + self.direction[0], direction[1] + self.direction[1]) != (0, 0):
            self.pending = direction

    def step(self):
        """Advance one tick. Returns False once the game is over."""
        self.direction = self.pending
        head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])

        if not (0 <= head[0] < WIDTH and 0 <= head[1] < HEIGHT):
            return False
        # the tail tip moves away this step, so it is not a collision
        if head in self.snake[:-1]:
            return False

        self.snake.insert(0, head)
        if head == self.apple:
            self.score += 1
            self.delay = max(MIN_DELAY, self.delay - SPEEDUP)
            self.apple = self.new_apple()
            if self.apple is None:
                self.won = True
                return False
        else:
            self.snake.pop()
        return True


def frame(game, paused, message=None):
    grid = [[" "] * WIDTH for _ in range(HEIGHT)]
    if game.apple:
        grid[game.apple[1]][game.apple[0]] = RED + "*" + RESET
    for index, (x, y) in enumerate(game.snake):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            grid[y][x] = GREEN + ("@" if index == 0 else "o") + RESET

    lines = ["+" + "-" * WIDTH + "+"]
    lines += ["|" + "".join(row) + "|" for row in grid]
    lines.append("+" + "-" * WIDTH + "+")

    speed = round((START_DELAY - game.delay) / SPEEDUP)
    status = f" score {game.score}   speed {speed}"
    if paused:
        status += "   [paused]"
    lines.append(status.ljust(WIDTH + 2))
    lines.append((message or " arrows/wasd move, p pause, q quit").ljust(WIDTH + 2))
    return HOME + "\n".join(lines) + "\n"


def draw(text):
    sys.stdout.write(text)
    sys.stdout.flush()


def play(reader):
    """Run one game. Returns True if the player wants another round."""
    game = Game()
    paused = False
    next_step = time.monotonic() + game.delay
    draw(frame(game, paused))

    while True:
        for key in reader.read():
            if key in ("q", "\x03"):
                return False
            if key == "p":
                paused = not paused
                draw(frame(game, paused))
            elif key in DIRECTIONS and not paused:
                game.turn(DIRECTIONS[key])

        now = time.monotonic()
        if paused:
            next_step = now + game.delay
            time.sleep(0.01)
            continue
        if now < next_step:
            time.sleep(min(0.005, next_step - now))
            continue

        next_step = now + game.delay
        if not game.step():
            break
        draw(frame(game, paused))

    outcome = "you filled the board!" if game.won else "game over"
    draw(frame(game, False, f" {outcome} score {game.score} - r replay, q quit"))
    while True:
        for key in reader.read():
            if key == "r":
                return True
            if key in ("q", "\x03"):
                return False
        time.sleep(0.02)


def main():
    columns, rows = shutil.get_terminal_size((80, 24))
    if columns < WIDTH + 2 or rows < HEIGHT + 4:
        sys.exit(f"Terminal too small, need at least {WIDTH + 2}x{HEIGHT + 4}.")

    enable_ansi()
    draw(CLEAR + HIDE_CURSOR)
    try:
        with KeyReader() as reader:
            while play(reader):
                pass
    except KeyboardInterrupt:
        pass
    finally:
        draw(SHOW_CURSOR + "\n")


if __name__ == "__main__":
    main()
