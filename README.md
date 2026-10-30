# cheezrun

A mouse wants cheese. We need a maze. I don't want to design it by hand every time.

One command generates a random maze for our little robot mice at ARTS.

```sh
maze 6 9
```

That's it. No menus, no dependencies, no unnecessary features.

- `6 9` and `9 6` both give a **9-wide x 6-high** maze.
- `M` is the mouse. `C` is the cheese.
- Fully enclosed. Always solvable.
- Avoids very long straight corridors and internal walls when possible.
- Every run generates a different maze.

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

Randomized Prim generates a connected layout, then we add a few loops and select one with reasonable corridors, walls, and a nontrivial route to the cheese. It's a heuristic, not a robotics simulator.

One Python file. No third-party packages.
