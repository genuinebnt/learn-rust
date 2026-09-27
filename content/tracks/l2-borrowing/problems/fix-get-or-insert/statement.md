Neither method compiles, though both are correct: this is a known limit of today's borrow checker.
Fix them without the entry API, without calling `make` on a hit, and without cloning any value.
