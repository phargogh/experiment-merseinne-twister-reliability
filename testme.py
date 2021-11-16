import random

random.seed(-1)

RAND_INT = random.randint(0, 100)
EXPECTED = 17  # what I'm getting on my ARM-based laptop
assert RAND_INT == EXPECTED, "%s != %s" % (RAND_INT, EXPECTED)
