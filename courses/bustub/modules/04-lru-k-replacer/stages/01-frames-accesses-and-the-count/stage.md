LRU forgets how a page was used the moment it is used again: one access and a hundred look the same. LRU-K remembers the last *k* accesses of each frame and judges a frame by the time since its k-th most recent access. This module builds it in three steps, and the first has nothing to do with k at all: the **bookkeeping that every replacer needs**. A pool tells the replacer when a frame is accessed, when it may be evicted and when it must not be, and asks for a victim. Get the contract right first; choose the policy afterwards.

> [!CHECK] The buffer pool calls `record_access(frame)` and then, a moment later, `set_evictable(frame, true)`. Why does the replacer start a new frame as *not* evictable instead of evictable? Think about what the pool is doing between those two calls.
> ||Between the calls the page is in use: it has just been read from disk or created and the caller holds it. A frame that could be evicted at that point could be taken away while its page is still being used. "Not evictable until told otherwise" is the safe default; the pool says "evictable" when the last user lets go.||
>
> - Who decides when a frame may be evicted: the replacer or the pool?
> - What would break if a new frame started evictable?
> - What does the replacer do with a request about a frame it has never heard of?

## The task

`LruKReplacer::new(num_frames, k)` makes a replacer for frames `0..num_frames` with history length `k`. In this stage the choice of victim is up to you (any evictable frame is acceptable); the next stage fixes the policy. The contract:

- `record_access(frame)`: notes an access at the current time and advances a logical clock by one. A frame seen for the first time becomes **tracked** and starts **not evictable**. A frame outside `0..num_frames` is a bug in the caller: **panic**.
- `set_evictable(frame, bool)`: changes whether a tracked frame may be evicted. A frame that is not tracked is ignored. Setting the value it already has changes nothing.
- `size()`: the number of **evictable** frames (not the number tracked).
- `evict()`: removes and returns one evictable frame, or `None` if none is evictable. The frame is **forgotten**, history included: it stops being tracked, and a later access starts it afresh.
- `remove(frame)`: forgets an evictable frame whatever its distance. An untracked frame is ignored. A tracked frame that is *not* evictable is a bug in the caller: **panic**.
- `k` of 0 is meaningless: `new` panics.

The tests run random sequences of all these operations against a model made of a map from frame to flag, and check the contract after every step: `size` is the evictable count, a victim is always an evictable frame and is gone afterwards, `None` only when nothing can be evicted.

## Your freedom

How frames and their histories are stored, and which evictable frame `evict` returns for now. Think ahead to the next stage: it will need the last `k` access times of each frame.

## The Rust toolbox

**A map of per-frame state.** `HashMap<FrameId, Node>` where `Node` holds the frame's flag and its history. `map.entry(frame).or_insert_with(|| Node::new(k))` gets the node for an access, creating it the first time, in one lookup.

**`let Some(x) = ... else { return };`** is the shortest way to say "ignore it if it is not there":

```rust
let Some(node) = self.nodes.get_mut(&frame) else { return };
node.evictable = evictable;
```

**Keeping a count in step.** `size()` is called often; counting by iterating is O(n). Keep a counter that changes exactly when a flag flips, and check it against the real count in a `debug_assert_eq!` while you develop: the model test would find a drift, but the assertion points at the line.

**`assert!` with a message for caller bugs, silence for harmless requests.** The line between them is "could a correct caller do this?". A pool may well ask about a frame that was just evicted, so ignore it; no correct caller removes a frame it is using, so panic.

**`VecDeque` for "the last k".** `push_back(t)` then `if len > k { pop_front(); }` keeps only the newest `k` timestamps and is O(1). `Vec::remove(0)` would shift every element.

## If this is new

- **S4 Maps & sets**: `HashMap`, `entry`, `get_mut`, `remove`.
- **S1 Option & Result**: `let ... else`, `?` on options, `Option::map`.
- **S3 Vec & slices** for `VecDeque` if you have not met it.

## Tests

- A new frame is not evictable; `size` counts evictable frames, each once.
- Evicting forgets the frame: marking it evictable afterwards does nothing, and a new access tracks it afresh.
- Unknown frames are ignored by `set_evictable` and `remove`; `remove` takes an evictable frame out.
- Misuse panics: `k = 0`, a frame out of range, removing a frame that is not evictable.
- For random sequences, the contract holds at every step.

## Hints

### What must a frame remember?

List what the policy of the next stage will need to know about a frame: its flag, and what else? Is it enough to store the time of the latest access? Work out what you would need to store for `k = 3`.

### Which operations change the count?

Write a table: for each of the five operations, say when `size` changes. Include the surprising ones: an access to an evictable frame, evicting, removing.

### Choosing a victim for now

Any evictable frame will do, and the cheapest correct choice is the first one you find. It is deliberately not the policy; the policy tests start in the next stage.

## Performance

Everything here is a hash lookup and a few integer operations: tens of nanoseconds. The only thing that can go wrong is `evict`, which in the simplest design scans all frames: O(n) per eviction. Stage 1d-03 makes it fast.

**Measure it.** With 100 000 frames all evictable, time 1 000 evictions followed by re-adding the frames. Multiply by 100 to see what the buffer pool would pay for 100 000 evictions.

## Experiment

Optional. Predict first, then run.

1. **The clock.** Why does the replacer keep its own clock instead of reading the system time? Replace your counter with `Instant::now()` and run the model test; what goes wrong, and what does it say about what a test can assume?
2. **A small `k`.** What does `k = 1` mean in the contract above, and what would you expect `evict` to return in the next stage when `k = 1`?

## Other designs

- **`HashMap<FrameId, Node>` (ours).** Sparse, flexible, one hash per call.
- **`Vec<Option<Node>>` indexed by frame id.** The frames are numbered `0..num_frames`, so a vector works and is faster; memory is proportional to the pool size whether or not frames are in use.
- **Separate maps for flag and history.** Smaller structs, but two lookups and two things to keep in step.

## In BusTub

```cpp
class LRUKReplacer {
 public:
  explicit LRUKReplacer(size_t num_frames, size_t k);
  auto Evict() -> std::optional<frame_id_t>;
  void RecordAccess(frame_id_t frame_id, AccessType access_type = AccessType::Unknown);
  void SetEvictable(frame_id_t frame_id, bool set_evictable);
  void Remove(frame_id_t frame_id);
  auto Size() -> size_t;
};
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::optional<frame_id_t> Evict()` | `fn evict(&mut self) -> Option<FrameId>` |
| `BUSTUB_ASSERT(cond, "msg")` / throwing for caller bugs | `assert!(cond, "msg")` |
| `std::unordered_map<frame_id_t, LRUKNode>` plus `std::mutex latch_` | `HashMap<FrameId, Node>`; `&mut self` makes the caller hold exclusive access |
| `std::list<size_t> history_` | `VecDeque<usize>` |

**Port rule:** a method that reports "none" through a `bool` and an out-parameter or an `optional` returns an `Option`; an internal mutex goes away when the methods take `&mut self`.

## Learn more

- [`HashMap::entry`](https://doc.rust-lang.org/std/collections/hash_map/enum.Entry.html) · [`let else`](https://doc.rust-lang.org/rust-by-example/flow_control/let_else.html) · [`VecDeque`](https://doc.rust-lang.org/std/collections/struct.VecDeque.html)
- O'Neil, O'Neil and Weikum, *The LRU-K page replacement algorithm for database disk buffering*, SIGMOD 1993
