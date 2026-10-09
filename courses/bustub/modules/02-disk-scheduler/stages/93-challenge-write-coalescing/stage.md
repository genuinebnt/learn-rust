A challenge: no walkthrough, no hints, no solution. Solve it with what this module and the ones before it taught. It is extra practice and does not count towards the course.

## What to build

`coalesce` in `src/storage/disk/coalesce.rs`: given a batch of disk operations (`Write(page, value)` and `Read(page)`) in the order they were submitted, return a batch that has **as few writes as possible** and produces exactly the same read results and the same final disk contents.

## Why

A scheduler that sees ten writes to the same page in its queue only needs to issue the last one, if nobody reads in between. Dropping the wrong write changes what a reader sees; dropping none wastes the disk. The exercise is finding exactly the writes that are safe to drop.

## The contract

- `coalesce(ops)` returns a new list of operations. Reads are kept, in order.
- A write may be dropped when a **later write to the same page** exists and **no read of that page lies between** them.
- The relative order of the operations that remain is the order they had.

## Invariants

These must hold after every step, whatever the input:

- Replaying the output on any starting disk gives the same read results, in the same order, as replaying the input.
- The final contents of every page are the same.
- The output contains every read of the input.

## Relations between input and output

How the answer must change when the input changes. The property tests check these on random inputs:

- No two writes to the same page are adjacent in the output with no read of that page between them.
- The output is never longer than the input, and `coalesce(coalesce(x)) == coalesce(x)`.
- A batch of only writes comes out with one write per page (the last value).

## Examples

Worked cases (the tests include them):

```text
W1=a W1=b W1=c -> W1=c
W1=a R1 W1=b -> unchanged (the read sees a)
W1=a W2=x W1=b -> W2=x W1=b
```

## What the tests check

- Writes only, reads between, interleaved pages.
- Empty batch and a single operation.
- A property: same read results and final state; idempotence; minimality.

## Done when

All the `s1b_c4` tests pass.
