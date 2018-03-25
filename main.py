import time

import pygame

from grid_draw import draw_grid_to
from colors import Color
import qclock
from utils import zipmul

from lib_mazegen import MazeGenerator

WIDTH   = 70
HEIGHT  = 70
BLOCK_SIZE = 10
INTERVAL = 0

if WIDTH * BLOCK_SIZE > 1920 or HEIGHT * BLOCK_SIZE > 1080:
    print("Window exceeds screen size")
    exit(1)

elemcolor = [
    Color.WHITE,     # Passage
    Color.BLACK,     # Wall
    Color.GREEN,     # Start
    Color.BLUE,      # End
    Color.RED,       # Marker
    Color.LPINK      # Light Marker
]

def create_screen():
    return pygame.display.set_mode(zipmul((WIDTH, HEIGHT), (BLOCK_SIZE, ) * 2))

class App:
    def __init__(self, width, height, *, screen=None, block_size=30, sparsiness=3, 
                                         interval=INTERVAL, find_route=False, random_pop=True):
        self.screen = screen
        self.generator = MazeGenerator(width, height, sparsiness, random_pop)
        self.block_size = block_size
        self.interval = interval
        self.interval_enabled = interval >= 0
        self.creation = None
        self.find_route = find_route
        self.creation_done = False
        self.endroute = []
        self.route_begin = (None, None)

    def run(self, screen=None):
        if self.screen is None and screen is None: 
            raise ValueError("Missing screen object for application.")
        elif self.screen is None and screen is not None:
            self.screen = screen

        if self.interval_enabled:
            self.creation = iter(self.generator.create())
            changed = []
        else:
            print("Creating maze... ", end="", flush=True)
            start = time.time()
            self.generator.create2()
            end = time.time()
            print("Done")
            print("Creation took {} seconds".format(round(end - start, 2)))
            self.creation_done = True
            changed = None
        color_override = set()
        tickclock = qclock.Clock(); tickclock.set_back(0.1)
        if not self.interval_enabled: tickclock.disable()
        done = False
        forced_tick = False
        force_refresh = True
        clock = pygame.time.Clock()
        painting = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                    done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return True
                    elif event.key == pygame.K_t and self.interval_enabled:
                        forced_tick = True
                    elif event.key == pygame.K_d:
                        if self.creation is not None:
                            for _ in self.creation: pass
                            tick_num = -1
                            changed = None
                            force_refresh = True
                            self.creation_done = True
                    elif event.key == pygame.K_o:
                        self.find_route = not self.find_route
                        self.endroute.clear()
                        color_override.clear()
                        force_refresh = True
                        color_grid = [[elemcolor[e] for e in row]
                                      for row in self.generator.data]
                        drawn_rects = draw_grid_to(self.screen, color_grid,
                                                   self.block_size, None)
                        pygame.display.flip()
                    elif event.key == pygame.K_p:
                        painting = not painting
                elif event.type == pygame.MOUSEBUTTONUP:
                    print("Mouse click")
                    mouse_click_pos = pygame.mouse.get_pos()
                    print("Click rx: {}, ry: {}".format(*mouse_click_pos))
                    col, row = mouse_click_pos[0] // self.block_size, mouse_click_pos[1] // self.block_size
                    print("Click col: {}, row: {}".format(col, row))
                    if not painting:
                        found = True
                        if self.generator.data[row][col]:
                            print("Clicked wall")
                            found = False
                            nlist = self.generator.next_to(col, row) + self.generator.next_to_diag(col, row)
                            for nx, ny in nlist:
                                if not self.generator.data[ny][nx]:
                                    print("Defaulted to col: {}, row: {}".format(nx, ny))
                                    col, row = nx, ny
                                    found = True
                                    break
                            else:
                                print("Found no valid neighbours")
                        if found:
                            self.endroute.clear()
                            color_override.clear()
                            self.route_begin = (col, row)
                    else:
                        e = self.generator.data[row][col]
                        if e == 0 or e == 1:
                            print("Set to " + ("wall" if not e else "passage"))
                            self.generator.data[row][col] = not e
                            changed = [(col, row)]
                            self.endroute = []
                            color_override.clear()
                            force_refresh = True
            pygame.event.pump()

            if self.interval_enabled and (forced_tick or tickclock.passed(self.interval)):
                tickclock.tick()
                forced_tick = False
                try:
                    tick_num, changed = next(self.creation)
                except StopIteration:
                    print("End iteration")
                    tickclock.disable()
                    self.creation = None
                    self.creation_done = True

            if self.creation_done and self.find_route and self.endroute == []:
                print("Finding route... ", end="", flush=True)
                result = self.generator.find_route(self.route_begin)
                if isinstance(result, list):
                    self.endroute = result
                    print("Found")
                    print("Drawing route")
                    #print(self.endroute)
                    for cx, cy in self.endroute:
                        if self.generator.data[cy][cx] not in (2, 3):
                            color_override.add(((cx, cy), Color.RED))
                    force_refresh = True
                    changed = None
                else:
                    print("No route found")
                    print("Drawing visited area")
                    if isinstance(result, set):
                        self.endroute = None
                        for cx, cy in result:
                            if self.generator.data[cy][cx] not in (2, 3):
                                color_override.add(((cx, cy), Color.PURPLEW))
                    changed = None
                    force_refresh = True

            if tickclock.disabled and not force_refresh:
                changed = []

            color_grid = [[elemcolor[e] for e in row] for row in self.generator.data]
            for oc, color in color_override:
                ox, oy = oc
                color_grid[oy][ox] = color
            drawn_rects = draw_grid_to(self.screen, color_grid, self.block_size, changed)
            if drawn_rects:
                pygame.display.update(drawn_rects)
            else:
                pygame.display.flip()
            force_refresh = False
            clock.tick(60)
        return False


if __name__ == "__main__":
    resetting = True
    while resetting:
        app = App(WIDTH, HEIGHT, block_size=BLOCK_SIZE, sparsiness=2, 
                                 find_route=True, random_pop=True)
        screen = create_screen()
        resetting = app.run(screen)
    pygame.quit()
