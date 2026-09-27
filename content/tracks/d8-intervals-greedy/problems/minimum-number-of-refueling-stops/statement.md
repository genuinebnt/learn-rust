A car drives east from position 0 to `target`, using one unit of fuel per unit of distance. It starts with
`start_fuel` and its tank has no limit. `stations[i] = (position, fuel)`, sorted by position; stopping
there adds all of that fuel. Return the fewest stops needed to reach `target`, or `None`. Arriving
anywhere with exactly 0 fuel left still counts.
