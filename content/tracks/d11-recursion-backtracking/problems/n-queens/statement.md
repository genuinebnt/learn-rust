Place `n` queens on an `n × n` chessboard so that no two attack each other: no two share a row, a column or a
diagonal. Return every such placement.

Write each board as `n` strings, one per row from the top, with `Q` for the queen and `.` for an empty square.
The boards can come in any order.

`n` goes up to 12. Trying every arrangement and checking it at the end is far too slow there: check each queen
as you place it.
