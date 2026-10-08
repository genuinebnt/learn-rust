---
title: Arenas and generational handles: linked structures without pointers
summary: Why a doubly linked list is awkward in safe Rust, how to build one from indices into a Vec, and how a generation counter makes a stale handle detectable.
minutes: 10
---
A cache needs a list where "move this element to the back" and "remove this element" are O(1) *given something that names the element*. C++ gets that for free: `std::list` plus an iterator saved in a hash map (`list.splice(list.end(), list, it)`). Rust has no direct equivalent, and the reason is instructive.

## Why `LinkedList` is not enough

`std::collections::LinkedList` has `push_back`, `pop_front` and iterators, but **no stable handle** to an element: you cannot say "remove *that* node" without walking the list to it. And the textbook doubly linked list wants each node to point at both neighbours, i.e. **shared ownership with cycles**, which safe Rust makes you pay for:

| approach | what you write | the catch |
|---|---|---|
| `Rc<RefCell<Node>>` with `Weak` back-pointers | a node owns `next`, weakly refers to `prev` | reference counts, run-time borrow checks, not `Send` |
| raw pointers and `unsafe` | what `std::list` does internally | you own every aliasing and lifetime proof |
| **an arena**: nodes in a `Vec`, linked by **index** | `prev: Option<usize>`, `next: Option<usize>` | none of the above; one new problem (below) |

The arena is the idiomatic answer: an index is a plain `usize`, so there are no pointers, no cycles of ownership, and everything is `Send`.

```svg
caption: A list A, B, C stored in a Vec. Slot 2 was freed (its generation went from 0 to 1) and sits on the free list; a handle (2, gen 0) to the old element there is now detectably stale. The links are indices, not pointers.
<svg viewBox="0 0 760 250" role="img" aria-label="An arena of four nodes with prev, next and generation fields, a free list and a stale handle">
<text class="dim sm" x="20" y="22">nodes: Vec&lt;Node&gt;</text>
<rect class="live" x="20" y="34" width="170" height="104" rx="5"/><text class="dim sm" x="30" y="54">index 0</text><text class="big" x="30" y="80">value A</text><text class="t-b sm" x="30" y="100">prev none</text><text class="t-b sm" x="30" y="116">next 1</text><text class="t-w sm" x="30" y="132">gen 0</text><rect class="live" x="200" y="34" width="170" height="104" rx="5"/><text class="dim sm" x="210" y="54">index 1</text><text class="big" x="210" y="80">value B</text><text class="t-b sm" x="210" y="100">prev 0</text><text class="t-b sm" x="210" y="116">next 3</text><text class="t-w sm" x="210" y="132">gen 0</text><rect class="free" x="380" y="34" width="170" height="104" rx="5"/><text class="dim sm" x="390" y="54">index 2</text><text class="t-w big" x="390" y="80">value None</text><text class="t-w sm" x="390" y="100">on the free list</text><text class="t-w sm" x="390" y="132">gen 1 (was 0)</text><rect class="live" x="560" y="34" width="170" height="104" rx="5"/><text class="dim sm" x="570" y="54">index 3</text><text class="big" x="570" y="80">value C</text><text class="t-b sm" x="570" y="100">prev 1</text><text class="t-b sm" x="570" y="116">next none</text><text class="t-w sm" x="570" y="132">gen 0</text><text class="dim sm" x="20" y="166">head = 0     tail = 3     free = [2]</text>
<rect class="hot" x="20" y="182" width="190" height="38" rx="4"/><text class="mid t-a sm" x="115" y="205">stale handle (index 2, gen 0)</text>
<path class="ln-w dash" d="M210 201 H420 V140" /><text class="t-w sm" x="430" y="184">gen 0 &#8800; gen 1: index_of returns None</text>
<rect class="live" x="540" y="182" width="190" height="38" rx="4"/><text class="mid t-g sm" x="635" y="205">live handle (index 3, gen 0)</text>
</svg>
```

## The one new problem: stale handles

A `usize` index stays *valid as a number* after its node is removed. If the slot is later reused for a different element, an old index now silently names the wrong one: the **ABA problem**, the same family of bug as a dangling pointer, just without the segfault. The fix is a **generation counter**: every node has a `generation: u32`, bumped each time the node is freed, and a handle carries both:

```rust
#[derive(Clone, Copy, PartialEq, Eq, Hash)]
pub struct Handle { index: usize, generation: u32 }

fn index_of(&self, h: Handle) -> Option<usize> {
    let node = self.nodes.get(h.index)?;
    (node.generation == h.generation && node.value.is_some()).then_some(h.index)
}
```

Now `remove(handle)` and `move_to_back(handle)` first check the generation: a handle to a removed element returns `None` or `false` instead of damaging whatever lives in the slot now. A `u32` generation wraps after four billion reuses of *one slot*, which is safe enough for a cache and worth stating in a comment.

## The free list

Freed nodes are not deallocated; their indices go on a `free: Vec<usize>` stack, and `push_back` pops from it before growing the `Vec`. That keeps handles (indices) stable while the list grows and shrinks. Compare: a `Vec` that `remove`d elements would shift everything and invalidate every index.

```rust
if let Some(free) = self.free.pop() {            // reuse a freed slot, keeping its generation
    node.generation = self.nodes[free].generation;
    self.nodes[free] = node;
    index = free;
} else {
    self.nodes.push(node);                        // or grow the arena
    index = self.nodes.len() - 1;
}
```

## The operations, as pointer surgery

`unlink(i)` is the heart: look up `prev` and `next`, make each point at the other (or move `head`/`tail` if one is `None`), then mark the node free and bump its generation. `move_to_back(h)` is `unlink` followed by a `push_back` that **keeps the handle valid** (same index and generation). Both are O(1), which is the whole point.

> [!PORT] C++
> `std::list<frame_id_t> lru_; std::unordered_map<frame_id_t, std::list<frame_id_t>::iterator> where_;`, with `lru_.splice(lru_.end(), lru_, where_[f])` to move to the back. List iterators stay valid until their element is erased, and *using one after* is undefined behaviour. The generational handle is the checked version of that iterator: misuse is an `Option::None`, not a crash.

> [!NOTE] Where else this pattern appears
> Entity-component systems in game engines, the `slotmap` and `generational-arena` crates, compiler IRs, and the buffer pool's frame ids. Whenever you would build a graph in C++ out of pointers, ask whether an arena and indices will do.
