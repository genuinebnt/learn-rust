Each ticket `(from, to)` is a flight. Starting at `"JFK"`, use every ticket exactly once. Of all the
itineraries that do, return the smallest one comparing airports in order (so at each choice, the
alphabetically smaller airport wins if it still leads to a full itinerary). The tickets always form at
least one valid itinerary. Recursion is fine: the large tests run with a big stack.
