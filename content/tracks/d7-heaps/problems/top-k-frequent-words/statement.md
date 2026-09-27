Return the `k` most frequent words, most frequent first. Words with the same count come in lexicographic
order (`str`'s own `Ord`, which compares bytes: `"B" < "a" < "é"`). If there are fewer than `k` different
words, return them all.
