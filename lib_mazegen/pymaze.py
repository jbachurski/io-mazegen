import random, itertools, collections
from heapq import heappush, heappop

def zipsum(a, b):
    return a[0] + b[0], a[1] + b[1]

def random_pop(seq):
    return seq.pop(random.randint(0, len(seq) - 1))

START = 0
DONE = 1

DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))
DIRS_DIAG = ((1, 1), (1, -1), (-1, -1), (-1, 1))
class MazeGenerator:
    def __init__(self, width, height, sparsiness=2, random_pop=True):
        assert width > 3 and height > 3
        self.width, self.height = width, height
        self.data = None
        self.fill_data(0)
        self.sparsiness = sparsiness
        self.start_pos = self.end_pos = None
        self.enable_random_stack_pop = random_pop

    def __repr__(self):
        return "MazeGenerator({}, {})".format(self.width, self.height) 

    def pprint(self):
        print("MazeGenerator {")
        print("Data:")
        for row in self.data:
            print("\t", end="")
            print(*row, sep=" ")
        print("}")

    def fill_data(self, obj):
        self.data = [[obj for _ in range(self.width)] for _ in range(self.height)]

    def count_neighbouring_walls(self, x, y):
        return sum(bool(self.data[iy][ix]) for ix, iy in (zipsum(d, (x, y)) for d in self.DIRS_DIAG))

    def is_border_wall(self, x, y):
        return any((x == 0 and 0 <= y < self.height,
                    x == self.width - 1 and 0 <= y < self.height,
                    y == 0 and 0 <= x < self.width,
                    y == self.width - 1 and 0 <= x < self.width))

    def is_in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def can_be_maze_part(self, x, y):
        return self.is_in_bounds(x, y) and not self.is_border_wall(x, y)

    def next_to(self, x, y, dirs=DIRS, with_ends=False):
        t = (x, y)
        result = []
        for d in dirs:
            cur = zipsum(t, d)
            cx, cy = cur
            if 0 < cx < self.width - 1 and 0 < cy < self.height - 1:
                result.append(cur)
            elif with_ends and cur in (self.start_pos, self.end_pos):
                result.append(cur)
        return result

    def next_to_diag(self, x, y, with_ends=False):
        return self.next_to(x, y, DIRS_DIAG, with_ends)

    def create_ends(self):
        pair = []
        used_walls = []
        while len(pair) < 2:
            wall = random.choice("udlr")
            if wall in used_walls: continue
            else: used_walls.append(wall)
            if wall == "l": pair.append((0, random.randint(1, self.height - 2)))
            if wall == "r": pair.append((self.width - 1, random.randint(1, self.height - 2)))
            if wall == "u": pair.append((random.randint(1, self.width - 2), 0))
            if wall == "d": pair.append((random.randint(1, self.width - 2), self.height - 1))
        self.start_pos, self.end_pos = pair
        self.data[self.start_pos[1]][self.start_pos[0]] = 2
        self.data[self.end_pos[1]][self.end_pos[0]] = 3

    def create(self):
        tick_counter = itertools.count(1)
        self.fill_data(1)
        if self.start_pos is None or self.end_pos is None: 
            self.create_ends()
        yield (next(tick_counter), START)

        if self.enable_random_stack_pop:
            vpop = lambda seq: random_pop(seq)
        else:
            vpop = lambda seq: list.pop(seq, -1)
        start_nxt = list(self.next_to(*self.start_pos))
        end_nxt = list(self.next_to(*self.end_pos))
        to_visit = []
        to_visit.extend(start_nxt)
        visited = set(start_nxt)
        while to_visit:
            current = vpop(to_visit)
            changed = []
            cx, cy = current
            next_to_d = self.next_to_diag(cx, cy)
            next_to = self.next_to(cx, cy)
            next_to_all = next_to + next_to_d
            part_next_d = sum(not self.data[n[1]][n[0]] for n in next_to_all)
            if part_next_d <= self.sparsiness:
                self.data[cy][cx] = 0
                changed.append(current)

                random.shuffle(next_to)
                for nxt in next_to:
                    if nxt not in visited:
                        to_visit.append(nxt)
                        visited.add(nxt)

            if changed:
                yield (next(tick_counter), changed)

        changed = []
        for n in end_nxt:
            self.data[n[1]][n[0]] = 0
            changed.append(n)
        if changed:
            yield next(tick_counter, changed)

        yield (next(tick_counter), DONE)

    def create2(self):
        for tick in self.create():
            pass

    def find_route_dfs(self, begin=(None, None)):
        if begin == (None, None): begin = self.start_pos
        stack = [(begin, [begin])]
        visited = {begin}
        while stack:
            current, croute = stack.pop()
            for n in self.next_to(*current, with_ends=True):
                if n in visited:
                    continue
                nx, ny = n
                if not self.data[ny][nx]:
                    stack.append((n, croute + [n]))
                    visited.add(n)
                if n == self.end_pos:
                    return croute + [n]
        return None

    def distance(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def find_route_astar(self, begin=(None, None)):
        if begin == (None, None): begin = self.start_pos
        end = self.end_pos
        print(begin, end)
        heap = [(self.distance(*begin, *end), (begin, [begin]))]
        visited = {begin}
        while heap:
            priority, pair = heappop(heap)
            current, croute = pair
            for n in self.next_to(*current, with_ends=True):
                #print("Next", n)
                if n in visited:
                    continue
                nx, ny = n
                if not self.data[ny][nx]:
                    heappush(heap, (self.distance(*n, *end), (n, croute + [n])))
                    visited.add(n)
                if n == end:
                    return croute + [n]
        return visited

    find_route = find_route_astar

if __name__ == "__main__":
    gen = MazeGenerator(20, 20)
    gen.create2()
