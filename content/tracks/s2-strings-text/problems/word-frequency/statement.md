Count the words read from `input`. A word is a whitespace-separated piece with leading and trailing
non-alphanumeric characters stripped, lowercased; pieces that end up empty don't count.

Return `(word, count)` pairs sorted by count descending, then alphabetically. Invalid UTF-8 in the
input is an error, not a panic.
