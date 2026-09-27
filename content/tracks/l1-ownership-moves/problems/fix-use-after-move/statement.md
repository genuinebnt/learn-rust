`describe` doesn't compile: it uses parts of `batch` after moving them. Fix it without cloning
anything. The items must come back to the caller as the same `Vec`, not a copy.

Some of the moves in `describe` are fine as they are. Change only the ones the compiler rejects.
