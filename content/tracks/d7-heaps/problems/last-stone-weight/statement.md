Each turn, take the two heaviest stones, `y ≥ x`, and smash them together: if `x == y` both are destroyed,
otherwise a stone of weight `y − x` goes back. Play until at most one stone is left.

Return the weight of the last stone, or `None` if every stone was destroyed.
