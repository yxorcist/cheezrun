"""Core invariants, independent of the random maze layout."""

import importlib.machinery
import importlib.util
import random
import unittest
from pathlib import Path

MAZE_PATH = Path(__file__).resolve().parents[1] / 'maze'
loader = importlib.machinery.SourceFileLoader('cheezrun_maze', str(MAZE_PATH))
spec = importlib.util.spec_from_loader(loader.name, loader)
maze = importlib.util.module_from_spec(spec)
loader.exec_module(maze)


class MazeTests(unittest.TestCase):
    def test_closed_solvable_and_rendered(self):
        for width, height in [(2, 2), (3, 7), (6, 9), (9, 6), (12, 12), (20, 7)]:
            w, h = max(width, height), min(width, height)
            for seed in range(12):
                with self.subTest(w=w, h=h, seed=seed):
                    grid, mouse, cheese = maze.generate(width, height, random.Random(seed))
                    self.assertEqual(len(grid), w * h)
                    self.assertNotEqual(mouse, cheese)
                    distances, previous = maze.distances(grid, w, h, mouse)
                    self.assertTrue(all(d >= 0 for d in distances))
                    path = maze.route(previous, mouse, cheese)
                    self.assertEqual(len(path), distances[cheese] + 1)
                    for a in range(len(grid)):
                        for b, direction, reverse in maze.neighbors(a, w, h):
                            self.assertEqual(bool(grid[a] & direction), bool(grid[b] & reverse))
                        x, y = a % w, a // w
                        if x == 0:
                            self.assertFalse(grid[a] & maze.W)
                        if x == w - 1:
                            self.assertFalse(grid[a] & maze.E)
                        if y == 0:
                            self.assertFalse(grid[a] & maze.N)
                        if y == h - 1:
                            self.assertFalse(grid[a] & maze.S)
                    output = maze.render(grid, w, h, mouse, cheese)
                    lines = output.splitlines()
                    self.assertEqual(len(lines), 2 * h + 1)
                    self.assertTrue(all(len(line) == 4 * w + 1 for line in lines))
                    self.assertEqual(output.count('M'), 1)
                    self.assertEqual(output.count('C'), 1)
                    self.assertEqual(lines[0], '+' + '---+' * w)
                    self.assertEqual(lines[-1], '+' + '---+' * w)

    def test_swapped_dimensions_generate_identical_maze_with_seed(self):
        a = maze.generate(6, 9, random.Random(42))
        b = maze.generate(9, 6, random.Random(42))
        self.assertEqual(a, b)

    def test_reject_invalid_sizes(self):
        for width, height in [(0, 6), (1, 10), (-3, 10), (41, 2), (2, 100)]:
            with self.subTest(width=width, height=height):
                with self.assertRaises(ValueError):
                    maze.generate(width, height, random.Random(0))

    def test_display_contains_no_open_perimeter(self):
        grid, mouse, cheese = maze.generate(9, 6, random.Random(5))
        lines = maze.render(grid, 9, 6, mouse, cheese).splitlines()
        self.assertTrue(all(line.startswith('|') and line.endswith('|') for line in lines[1::2]))


if __name__ == '__main__':
    unittest.main()
