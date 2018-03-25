import cProfile
import pstats
import time
from cymaze.maze import MazeGenerator

generator = MazeGenerator(1000, 1000, 2)

#code = """
#for tick in generator.create():
#    pass
#""".strip()
#cProfile.run(code, "profileresults")

start = time.time()
pr = cProfile.Profile()
pr.enable()
for tick in generator.create():
    pass
pr.disable()
end = time.time()
pr.dump_stats("profileresults")

profile = pstats.Stats("profileresults")
profile.strip_dirs().sort_stats("time").print_stats()
print("Primitive timer: {} seconds".format(round(end - start, 3)))
#generator.pprint()
