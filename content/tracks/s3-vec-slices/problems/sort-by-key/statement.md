- `sort_files(files)`: order by extension (the text after the last `.`), ignoring ASCII case, with files
  that have no extension first; within an extension, largest first. Files that tie on both keep their input
  order. This runs on directories of thousands of files: don't allocate on every comparison.
- `leaderboard(players)`: `(name, wins, losses)`. Most wins first, then fewest losses, then by name. Names
  are unique, so there are no ties.
- `sort_readings(v)`: ascending in IEEE 754 total order, which places `-0.0` before `0.0`, infinities at the
  ends and NaN after `+inf`. Readings may contain NaN.
