"""Core invariants, independent of the random maze layout."""

import importlib.machinery
import importlib.util
import random
import re
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
                    grid, mouse, cheese, facing = maze.generate(width, height, random.Random(seed))
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
                    self.assertIn('M' + maze.HEADING_LABELS[facing], output)
                    self.assertTrue(lines[0].startswith('┌') and lines[0].endswith('┐'))
                    self.assertTrue(lines[-1].startswith('└') and lines[-1].endswith('┘'))
                    self.assertNotIn('+', output)
                    self.assertTrue(all(lines[y].startswith('│') and lines[y].endswith('│')
                                        for y in range(1, len(lines), 2)))

    def test_wall_parts_cover_every_edge_once(self):
        for width, height in [(2, 2), (6, 9), (12, 5), (40, 3)]:
            w, h = max(width, height), min(width, height)
            for seed in range(8):
                grid, _, _, _ = maze.generate(w, h, random.Random(seed))
                target_h, target_v = maze.wall_edges(grid, w, h)
                found_h = [[False] * w for _ in range(h + 1)]
                found_v = [[False] * (w + 1) for _ in range(h)]
                for orientation, x, y, length in maze.wall_pieces(grid, w, h):
                    self.assertIn(length, (1, 2))
                    self.assertIn(orientation, ('H', 'V'))
                    for offset in range(length):
                        if orientation == 'H':
                            self.assertFalse(found_h[y][x + offset])
                            found_h[y][x + offset] = True
                        else:
                            self.assertFalse(found_v[y + offset][x])
                            found_v[y + offset][x] = True
                self.assertEqual(found_h, target_h)
                self.assertEqual(found_v, target_v)

    def test_color_keeps_same_geometry(self):
        w, h = 9, 6
        grid, mouse, cheese, facing = maze.generate(w, h, random.Random(9))
        plain = maze.render(grid, w, h, mouse, cheese, color=False)
        colored = maze.render(grid, w, h, mouse, cheese, color=True)
        self.assertIn('\x1b[96m', colored)
        self.assertIn('\x1b[92mM', colored)
        self.assertIn('\x1b[93mC', colored)
        self.assertEqual(re.sub(r'\x1b\[[0-9;]*m', '', colored), plain)

    def test_swapped_dimensions_generate_identical_maze_with_seed(self):
        a = maze.generate(6, 9, random.Random(42))
        b = maze.generate(9, 6, random.Random(42))
        self.assertEqual(a, b)

    def test_reject_invalid_sizes(self):
        for width, height in [(0, 6), (1, 10), (-3, 10), (41, 2), (2, 100)]:
            with self.subTest(width=width, height=height):
                with self.assertRaises(ValueError):
                    maze.generate(width, height, random.Random(0))

    def test_robot_program_is_valid_and_at_most_40_buttons(self):
        for w, h in [(2, 2), (3, 7), (6, 9), (9, 6), (12, 12), (20, 7), (40, 40)]:
            seeds = range(3) if w * h > 500 else range(12)
            for seed in seeds:
                with self.subTest(w=w, h=h, seed=seed):
                    width = max(w, h)
                    grid, mouse, cheese, facing = maze.generate(w, h, random.Random(seed))
                    commands = maze.program_to(grid, width, mouse, facing, cheese)
                    self.assertLessEqual(len(commands), maze.MAX_COMMANDS)
                    self.assertGreater(len(commands), 0)
                    self.assertTrue(set(commands) <= {'F', 'B', 'L', 'R'})
                    final_cell, _ = maze.execute(grid, width, mouse, facing, commands)
                    self.assertEqual(final_cell, cheese)
                    distances, _ = maze.command_distances(grid, width, mouse, facing)
                    self.assertEqual(len(commands), min(distances[cheese * 4: cheese * 4 + 4]))

    def test_backward_and_rotation_commands_are_real_buttons(self):
        grid = [maze.E, maze.W]
        # Mouse at left, facing west: B is one command to reach right.
        self.assertEqual(maze.program_to(grid, 2, 0, 3, 1), ['B'])
        self.assertEqual(maze.execute(grid, 2, 0, 3, ['B']), (1, 3))
        self.assertEqual(maze.execute(grid, 2, 0, 0, ['R', 'F']), (1, 1))
        with self.assertRaises(ValueError):
            maze.execute(grid, 2, 0, 0, ['F'])

    def test_cli_minimal_and_seeded_solution(self):
        import io
        import contextlib
        for args in (['6', '9', '1234'], ['9', '6', '1234']):
            with contextlib.redirect_stdout(io.StringIO()) as stream:
                result = maze.main(args)
            self.assertEqual(result, 0)
            lines = stream.getvalue().splitlines()
            self.assertEqual(len(lines), 13)
            self.assertTrue(all(len(line) == 37 for line in lines))
            if args[0] == '6':
                first = stream.getvalue()
            else:
                self.assertEqual(first, stream.getvalue())
        with contextlib.redirect_stdout(io.StringIO()) as stream:
            result = maze.main(['6', '9', '1234', 'solve'])
        self.assertEqual(result, 0)
        self.assertIn('Program (', stream.getvalue())
        self.assertIn('F=forward', stream.getvalue())

    def test_display_contains_no_open_perimeter(self):
        grid, mouse, cheese, facing = maze.generate(9, 6, random.Random(5))
        lines = maze.render(grid, 9, 6, mouse, cheese).splitlines()
        self.assertTrue(all(line.startswith('│') and line.endswith('│') for line in lines[1::2]))


if __name__ == '__main__':
    unittest.main()
