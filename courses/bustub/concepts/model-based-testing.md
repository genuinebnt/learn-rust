---
title: Model-based testing: checking a clever structure against a simple one
summary: Compare your fast data structure with an obviously correct, slow one over thousands of random operations from a fixed seed, and shrink a failure to the step that caused it.
minutes: 8
---
You can test an LRU-K replacer with a dozen hand-written cases, and they will all pass while a bug waits in the thousandth operation. The reliable method for data structures is **model-based testing** (a form of property testing): run the same random operations on the real structure and on a *model*, and compare after every step.

## The model is the slow, obvious version

A model should be so simple that you can see it is right:

```rust
/// A deliberately naive LRU-K: the same rules, one linear scan per eviction.
struct NaiveLruK { k: usize, now: usize, frames: HashMap<usize, (Vec<usize>, bool)> }

fn evict(&mut self) -> Option<usize> {
    let k = self.k;
    let victim = self.frames.iter()
        .filter(|(_, (_, evictable))| *evictable)
        .min_by_key(|(&frame, (history, _))| if history.len() < k { (0, history[0], frame) } else { (1, history[0], frame) })
        .map(|(&frame, _)| frame)?;
    self.frames.remove(&victim);
    Some(victim)
}
```

It is O(n) per eviction, which does not matter: the model only ever sees a few thousand operations. What matters is that its rules are the *specification*, written the dullest possible way.

## The loop

```rust
let mut rng = Lcg(1000 + k as u64);                  // a fixed seed: the run is reproducible
for step in 0..4000 {
    let frame = (rng.next() % 48) as usize;
    match rng.next() % 10 {
        0..=4 => { fast.record_access(f(frame)); slow.record(frame); }
        5..=7 => { let on = rng.next() % 2 == 0; fast.set_evictable(f(frame), on); /* mirror on the model */ }
        _     => assert_eq!(fast.evict().map(|x| x.0), slow.evict(), "k={k}, step {step}: the two disagree about the victim"),
    }
    assert_eq!(fast.size(), slow.size(), "k={k}, step {step}: the evictable counts differ");
}
```

Four habits make this useful rather than a lottery:

- **A fixed seed, and a message that names it.** A failure prints `k=3, step 2711`, and the same seed reproduces it exactly. A random test you cannot replay is noise.
- **Compare after every step**, not at the end. The first disagreement is the bug; by the end the state has diverged beyond reading.
- **A weighted operation mix.** If evictions are rare the structure never gets deep; if they are common it stays empty. Bias towards the operations that build state (`record_access`) and keep a steady share of the destructive ones.
- **Small domains.** 48 frames and 4000 steps hit the same frame hundreds of times, which is where state-dependent bugs live. A domain of a million never revisits anything.

## A tiny random generator, no crate needed

```rust
struct Lcg(u64);
impl Lcg {
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        self.0 >> 33
    }
}
```

A linear congruential generator is statistically weak and perfect for this: deterministic, ten lines, no dependency. (The low bits of an LCG are the least random, which is why the code shifts them away.)

## Finding the smallest failing case

When the models disagree, the output is a seed and a step number. To *understand* it: print the operations leading up to the step, then **shrink**: delete operations from the front one by one and re-run until removing any more makes the failure vanish. What remains is usually five or six lines and names the bug. Crates such as `proptest` automate this; doing it by hand once teaches what they do.

## Where this course uses it

| stage | model |
|---|---|
| LRU-K, O(log n) evict | the naive scan above |
| IndexList and the replacers | a `Vec` / `VecDeque` |
| the hash table (module 2b) | a `HashMap` |
| the B+ tree (module 2c) | a `BTreeMap` (the one in `std` *is* a B-tree) |

> [!TIP] The model is also documentation
> If you cannot write the model in ten lines, you do not yet understand the specification. Writing it first, before the clever version, is a good way to find that out.
