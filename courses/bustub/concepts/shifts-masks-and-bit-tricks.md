---
title: Shifts, masks and bit tricks on u32
summary: Keep the top k bits, keep the low k bits, flip a bit, and the edge case at the full width that panics in Rust and is undefined behaviour in C and C++.
minutes: 8
---
A hash table that doubles its directory is mostly bit arithmetic: *which* bits of the hash choose the directory, which choose the slot, and which single bit distinguishes two buckets that are about to split or merge. Four operations cover all of it.

## The four operations

| goal | expression | example, `x = 0b1011_0110`, `k = 3` |
|---|---|---|
| keep the **top** `k` bits of a `u32` (as a number) | `x >> (32 - k)` | for a `u32` `0xB600_0000`: `0b101` = 5 |
| keep the **low** `k` bits | `x & ((1 << k) - 1)` | `0b0110` masked with `0b0111` = 6 |
| a mask of `k` ones | `(1u32 << k) - 1` | `k = 3`: `0b0111` |
| **flip** bit `b` | `x ^ (1 << b)` | flipping bit 2 of `0b110` gives `0b010` |
| test bit `b` | `x & (1 << b) != 0` | |

`x >> n` drops the low `n` bits and brings in zeros (for unsigned types); `x << n` does the reverse. `&` keeps the bits where the mask has a one; `^` (xor) flips them.

```svg
caption: Four operations on the 8-bit value 10110110 with k = 3. Shifting right by (8 - k) keeps the top 3 bits; masking with 0b111 keeps the low 3; xor with a one-bit mask flips that bit. Highlighted cells are the bits each result is made of.
<svg viewBox="0 0 760 270" role="img" aria-label="Bit diagrams for taking the top bits, the low bits and flipping a bit">
<text class="big" x="20" y="37">x</text><rect class="box" x="190" y="20" width="30" height="26" rx="3"/><text class="mid fg" x="205" y="38">1</text><rect class="box" x="224" y="20" width="30" height="26" rx="3"/><text class="mid fg" x="239" y="38">0</text><rect class="box" x="258" y="20" width="30" height="26" rx="3"/><text class="mid fg" x="273" y="38">1</text><rect class="box" x="292" y="20" width="30" height="26" rx="3"/><text class="mid fg" x="307" y="38">1</text><rect class="box" x="326" y="20" width="30" height="26" rx="3"/><text class="mid fg" x="341" y="38">0</text><rect class="box" x="360" y="20" width="30" height="26" rx="3"/><text class="mid fg" x="375" y="38">1</text><rect class="box" x="394" y="20" width="30" height="26" rx="3"/><text class="mid fg" x="409" y="38">1</text><rect class="box" x="428" y="20" width="30" height="26" rx="3"/><text class="mid fg" x="443" y="38">0</text>
<text class="big" x="20" y="81">x >> 5</text><rect class="box" x="190" y="64" width="30" height="26" rx="3"/><text class="mid fg" x="205" y="82">0</text><rect class="box" x="224" y="64" width="30" height="26" rx="3"/><text class="mid fg" x="239" y="82">0</text><rect class="box" x="258" y="64" width="30" height="26" rx="3"/><text class="mid fg" x="273" y="82">0</text><rect class="box" x="292" y="64" width="30" height="26" rx="3"/><text class="mid fg" x="307" y="82">0</text><rect class="box" x="326" y="64" width="30" height="26" rx="3"/><text class="mid fg" x="341" y="82">0</text><rect class="live" x="360" y="64" width="30" height="26" rx="3"/><text class="mid fg" x="375" y="82">1</text><rect class="live" x="394" y="64" width="30" height="26" rx="3"/><text class="mid fg" x="409" y="82">0</text><rect class="live" x="428" y="64" width="30" height="26" rx="3"/><text class="mid fg" x="443" y="82">1</text>
<text class="t-g sm" x="470" y="82">top 3 bits as a number = 5</text>
<text class="big" x="20" y="125">x &amp; 0b111</text><rect class="box" x="190" y="108" width="30" height="26" rx="3"/><text class="mid fg" x="205" y="126">0</text><rect class="box" x="224" y="108" width="30" height="26" rx="3"/><text class="mid fg" x="239" y="126">0</text><rect class="box" x="258" y="108" width="30" height="26" rx="3"/><text class="mid fg" x="273" y="126">0</text><rect class="box" x="292" y="108" width="30" height="26" rx="3"/><text class="mid fg" x="307" y="126">0</text><rect class="box" x="326" y="108" width="30" height="26" rx="3"/><text class="mid fg" x="341" y="126">0</text><rect class="hot" x="360" y="108" width="30" height="26" rx="3"/><text class="mid fg" x="375" y="126">1</text><rect class="hot" x="394" y="108" width="30" height="26" rx="3"/><text class="mid fg" x="409" y="126">1</text><rect class="hot" x="428" y="108" width="30" height="26" rx="3"/><text class="mid fg" x="443" y="126">0</text>
<text class="t-a sm" x="470" y="126">low 3 bits = 6</text>
<text class="big" x="20" y="169">x ^ (1 &lt;&lt; 2)</text><rect class="box" x="190" y="152" width="30" height="26" rx="3"/><text class="mid fg" x="205" y="170">1</text><rect class="box" x="224" y="152" width="30" height="26" rx="3"/><text class="mid fg" x="239" y="170">0</text><rect class="box" x="258" y="152" width="30" height="26" rx="3"/><text class="mid fg" x="273" y="170">1</text><rect class="box" x="292" y="152" width="30" height="26" rx="3"/><text class="mid fg" x="307" y="170">1</text><rect class="box" x="326" y="152" width="30" height="26" rx="3"/><text class="mid fg" x="341" y="170">0</text><rect class="free" x="360" y="152" width="30" height="26" rx="3"/><text class="mid fg" x="375" y="170">0</text><rect class="box" x="394" y="152" width="30" height="26" rx="3"/><text class="mid fg" x="409" y="170">1</text><rect class="box" x="428" y="152" width="30" height="26" rx="3"/><text class="mid fg" x="443" y="170">0</text>
<text class="t-w sm" x="470" y="170">bit 2 flipped: 1 becomes 0</text>
<text class="dim sm" x="190" y="12">bit 7 ... bit 0</text>
<text class="t-r sm" x="20" y="214">x &gt;&gt; 8 on a u8:  panic in debug, x in release, undefined in C: the width is the edge</text>
<text class="dim sm" x="20" y="236">(the diagram uses 8 bits so it fits; the course's hashes are 32 bits)</text>
</svg>
```

## The edge: shifting by the full width

What is `x >> 32` for a `u32`? Not 0, in any of the three languages:

| language | `x >> 32` on a 32-bit value |
|---|---|
| **C, C++** | undefined behaviour. x86 masks the shift count to 5 bits, so you get `x >> 0 = x`; ARM behaves differently |
| **Rust, debug** | panic: `attempt to shift right with overflow` |
| **Rust, release** | masked like x86: `x >> 0 = x` |

So `hash >> (32 - max_depth)` is wrong at `max_depth == 0` (a shift by 32): the table with a single directory. The obvious C++, `hash >> (32 - max_depth_)`, is **wrong in a way no test catches**: on x86 it returns the whole hash instead of 0, which usually happens to index a slot out of range later. Rust shows the bug as a panic. Three fixes: a `match` arm for 0, `checked_shr` (returns `None` for a shift of 32 or more) with `unwrap_or(0)`, or an arithmetic trick (`(x as u64 >> (32 - k)) as u32` works because a `u64` shift by 32 is defined).

## Why the *top* bits for the header and the *low* bits for the directory

An extendible hash table uses **different ends of the hash at different levels**:

- the **header** takes the *top* `max_depth` bits, fixed forever, to pick one of up to 512 directories;
- each **directory** takes the *low* `global_depth` bits, which *grow by one* when the directory doubles.

Growing by the **low** end means a doubling is an *append*: the new directory entries `[n, 2n)` mirror the old ones `[0, n)`, because the entry for low bits `b` is the same as for `b + n` until a split distinguishes them. Growing at the top would force the directory to renumber every entry. And using the *opposite* end for the header means the two levels never consume the same bits.

## Split images and the bit that differs

Two buckets that were one before a split differ in exactly one bit of their directory index: bit `local_depth - 1`. So the **split image** of slot `i` at local depth `d` is `i ^ (1 << (d - 1))`:

```rust
pub fn get_split_image_index(&self, bucket_idx: u32) -> u32 {
    match self.get_local_depth(bucket_idx) {
        0 => bucket_idx,                                  // depth 0: no sibling, it is its own image
        depth => bucket_idx ^ (1 << (depth - 1)),
    }
}
```

At depth 0 there is no bit to flip, and `1 << (0 - 1)` would underflow: the same full-width edge from the other direction.

> [!PORT] Signedness
> `>>` on a **signed** integer is an *arithmetic* shift (it copies the sign bit in) in Rust, and implementation-defined in C++ before C++20. A hash is a bit pattern, not a number: use `u32`/`u64`, and cast with `as u32` *before* shifting if you start from an `i32`.
