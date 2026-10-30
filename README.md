# cheezrun

A mouse wants cheese. We need a maze. I don't want to design it by hand every time.

One command generates a random maze for our little robot mice at ARTS.

```sh
maze 6 9
```

That's it. No menus, no dependencies, no unnecessary features. The result uses UTF-8 box drawing, which works in Termux. Colors are automatic in terminals; use `NO_COLOR=1 maze 6 9` to switch them off.

- `6 9` and `9 6` both give a **9-wide x 6-high** maze.
- `M↑`, `M→`, `M↓`, or `M←` is the mouse and its starting direction. `C` is the cheese.
- Fully enclosed. Always solvable with **40 button presses or fewer**.
- Robot commands are real button presses: forward, backward, rotate left, rotate right.
- The generator prefers puzzles with a longer program, turns, and actual choices.
- Cyan walls, green mouse, yellow cheese in an interactive terminal.
- No pillar pieces. Every physical wall can be made from length-1 or length-2 edges; continuous runs are split into those pieces. The box-drawing junctions are just visual connections, not additional components.
- Avoids very long straight corridors and internal walls when possible.
- Every run generates a different maze (unless you supply a seed).

## Teacher's answer key

Optional. The default command only prints the maze.

```sh
maze 6 9 1234         # same maze every time
maze 6 9 1234 solve   # show the shortest button sequence
maze 6 9 solve        # random maze + its solution
```

Program: F=forward, B=backward, L=turn left, R=turn right. Turns rotate the mouse in place. The robot doesn't think for itself; children enter the instructions before pressing GO.

A cell corresponds to one 12.5 cm forward/backward movement on the actual robot. The physical board must match that step length for the instructions to work.

## Install

Requires Python 3.10+ and Git. On Termux:

```sh
pkg install python git
git clone https://github.com/yxorcist/cheezrun.git
cd cheezrun
sh install.sh
maze 6 9
```

On Linux, use the same steps after installing Python 3 and Git. If the shell cannot find `maze`, add `~/.local/bin` to your `PATH`.

Or skip installation and run `python3 maze 6 9` inside the repo.

## Development

```sh
python3 -m unittest discover -s tests -v
```

Randomized Prim generates connected layouts with a few loops. We score candidates for short walls, intersections, turns, and solvable button sequences. BFS over `(square, facing)` finds the minimum button count, including backward moves and 90-degree rotations. No program exceeds 40 presses. These are software guarantees; real-world driving accuracy still depends on the board and batteries.

One Python file. No third-party packages.
