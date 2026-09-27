Return how many ways there are to place `n` queens on an `n × n` chessboard so that no two attack each other (no two
in the same row, column or diagonal).

`n` goes up to 14 (365 596 solutions). Checking a new queen against every earlier queen is too slow there: each
check has to be O(1).
