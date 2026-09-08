"""Mini snake game for the terminal. Standard library only.

Run with: python snake.py
Controls: arrow keys or WASD to steer, p to pause, q to quit.
"""

import curses
import random

WIDTH = 30
HEIGHT = 18
START_LENGTH = 4
START_DELAY = 120      # milliseconds between steps
MIN_DELAY = 55
SPEEDUP = 4            # milliseconds shaved off per apple

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

KEYS = {
    curses.KEY_UP: UP, ord("w"): UP, ord("W"): UP,
    curses.KEY_DOWN: DOWN, ord("s"): DOWN, ord("S"): DOWN,
    curses.KEY_LEFT: LEFT, ord("a"): LEFT, ord("A"): LEFT,
    curses.KEY_RIGHT: RIGHT, ord("d"): RIGHT, ord("D"): RIGHT,
}


def new_apple(snake):
    free = [(x, y) for x in range(WIDTH) for y in range(HEIGHT) if (x, y) not in snake]
    return random.choice(free) if free else None


def draw(win, snake, apple, score, delay, paused):
    win.erase()
    win.box()

    for index, (x, y) in enumerate(snake):
        char = "@" if index == 0 else "o"
        win.addstr(y + 1, x + 1, char, curses.color_pair(1))

    if apple:
        win.addstr(apple[1] + 1, apple[0] + 1, "*", curses.color_pair(2))

    speed = (START_DELAY - delay) // SPEEDUP
    win.addstr(0, 2, f" score {score}  speed {speed} ")
    if paused:
        win.addstr(HEIGHT + 1, 2, " paused ")
    win.refresh()


def game_over(win, score):
    message = f"game over - score {score}"
    win.addstr(HEIGHT // 2, max(1, (WIDTH - len(message)) // 2 + 1), message)
    prompt = "r to replay, q to quit"
    win.addstr(HEIGHT // 2 + 1, max(1, (WIDTH - len(prompt)) // 2 + 1), prompt)
    win.refresh()
    win.nodelay(False)
    while True:
        key = win.getch()
        if key in (ord("r"), ord("R")):
            return True
        if key in (ord("q"), ord("Q"), 27):
            return False


def play(win):
    head = (WIDTH // 2, HEIGHT // 2)
    snake = [(head[0] - i, head[1]) for i in range(START_LENGTH)]
    direction = RIGHT
    pending = direction
    apple = new_apple(snake)
    score = 0
    delay = START_DELAY
    paused = False

    win.nodelay(True)
    win.timeout(delay)

    while True:
        draw(win, snake, apple, score, delay, paused)

        key = win.getch()
        if key in (ord("q"), ord("Q")):
            return False
        if key in (ord("p"), ord("P")):
            paused = not paused
            continue
        if key in KEYS:
            wanted = KEYS[key]
            # ignore a reversal straight into the neck
            if (wanted[0] + direction[0], wanted[1] + direction[1]) != (0, 0):
                pending = wanted

        if paused:
            continue

        direction = pending
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        hit_wall = not (0 <= head[0] < WIDTH and 0 <= head[1] < HEIGHT)
        # the tail tip moves away this step, so it is not a collision
        hit_self = head in snake[:-1]
        if hit_wall or hit_self:
            draw(win, snake, apple, score, delay, paused)
            return game_over(win, score)

        snake.insert(0, head)
        if head == apple:
            score += 1
            apple = new_apple(snake)
            if apple is None:
                draw(win, snake, apple, score, delay, paused)
                return game_over(win, score)
            delay = max(MIN_DELAY, delay - SPEEDUP)
            win.timeout(delay)
        else:
            snake.pop()


def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)

    rows, cols = stdscr.getmaxyx()
    if rows < HEIGHT + 2 or cols < WIDTH + 2:
        raise SystemExit(f"Terminal too small, need at least {WIDTH + 2}x{HEIGHT + 2}")

    win = curses.newwin(HEIGHT + 2, WIDTH + 2, (rows - HEIGHT - 2) // 2, (cols - WIDTH - 2) // 2)
    win.keypad(True)

    while play(win):
        pass


if __name__ == "__main__":
    curses.wrapper(main)
