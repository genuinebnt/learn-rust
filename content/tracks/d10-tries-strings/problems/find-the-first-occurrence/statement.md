Return the index of the first place `needle` occurs in `haystack`, or `None` if it never does.
An empty `needle` occurs at index 0.

Both are slices of any comparable type: bytes, characters, numbers. `str::find` is not available on slices,
and checking every window is too slow for the largest inputs.
