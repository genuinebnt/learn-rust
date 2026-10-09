A challenge: no walkthrough, no hints, no solution. It is extra practice and does not count towards the course.

## What to build

Nothing new. `src/rust_primer/rle.rs` has a complete run-length codec: `aaab` becomes the pairs (3, a) (1, b). It looks right, and it has one bug. Find it with the tests, and fix it.

## Why

Most real debugging starts from a failing test and a counterexample, not from reading code. A property test that fails prints the *smallest* input it could find that breaks the rule, and that input is usually the whole bug report. Reading a shrunk counterexample well is a skill worth practising on something small.

## The contract

`rle_encode` turns data into (count, byte) pairs with counts from 1 to 255, and `rle_decode` turns them back. Decoding the encoding of any data gives that data back.

## What the tests check

- The exact pairs for small inputs and for the longest run one pair can hold.
- That data comes back after a round trip, whatever its runs look like.
- That the encoding is well formed and its counts add up to the length of the data.
- That bad input to the decoder is an error.

## Done when

All the `sr_c2` tests pass, and you can say in one sentence what the bug was.
