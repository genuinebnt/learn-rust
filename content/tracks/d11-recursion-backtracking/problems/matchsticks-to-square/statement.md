`matchsticks[i]` is the length of a matchstick. Use every matchstick exactly once, without breaking any, to make
the four sides of a square. Sticks can be joined end to end within a side. Return `true` if it can be done.

Lengths go up to 10⁹ and there can be 20 sticks, so the total doesn't fit in a `u32`. The tests include inputs
where trying the sticks in the given order takes far too long.
