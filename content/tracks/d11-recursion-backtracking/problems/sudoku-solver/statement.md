`board` is a 9 × 9 Sudoku: `1` to `9` are given digits and `0` is an empty cell. Fill every empty cell so that each
row, each column and each of the nine 3 × 3 boxes holds the digits 1 to 9 once each, and return `true`.

If that's impossible, including when two givens already clash, return `false` and leave `board` as it was. When a
puzzle has more than one solution, any one of them is accepted.

The tests include puzzles built to defeat backtracking that fills cells in reading order: pick the next cell with
more care.
