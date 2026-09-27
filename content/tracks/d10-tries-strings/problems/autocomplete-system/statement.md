A search box suggests past sentences while the user types. `new(sentences, times)` loads each sentence with how
many times it was typed before. Then `input(c)` is called once per keystroke:

- for a letter or a space, return the three **hottest** past sentences that start with everything typed since the
  last `'#'`: highest count first, ties in ASCII order (a space sorts before letters). Fewer if fewer match;
- for `'#'`, the sentence typed so far is finished: add 1 to its count (it may be new), start a fresh sentence,
  and return an empty list.

Sentences are lowercase letters and spaces.
