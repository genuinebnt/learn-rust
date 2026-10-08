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

## In real code

### Using it: a complete, runnable generational arena list

The whole data structure (small enough to read in one sitting), with a test that shows every property the stage checks: O(1) removal by handle, slot reuse, and a stale handle that is rejected.

```rust test
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Handle { index: usize, generation: u32 }

struct Node<T> { value: Option<T>, prev: Option<usize>, next: Option<usize>, generation: u32 }

struct IndexList<T> { nodes: Vec<Node<T>>, head: Option<usize>, tail: Option<usize>, free: Vec<usize>, len: usize }

impl<T> IndexList<T> {
    fn new() -> Self { IndexList { nodes: Vec::new(), head: None, tail: None, free: Vec::new(), len: 0 } }

    fn index_of(&self, h: Handle) -> Option<usize> {
        let n = self.nodes.get(h.index)?;
        (n.generation == h.generation && n.value.is_some()).then_some(h.index)      // the generation check
    }

    fn push_back(&mut self, value: T) -> Handle {
        let mut node = Node { value: Some(value), prev: self.tail, next: None, generation: 0 };
        let index = if let Some(i) = self.free.pop() {                              // reuse a freed slot (keep its generation)
            node.generation = self.nodes[i].generation;
            self.nodes[i] = node;
            i
        } else {
            self.nodes.push(node);
            self.nodes.len() - 1
        };
        match self.tail { Some(t) => self.nodes[t].next = Some(index), None => self.head = Some(index) }
        self.tail = Some(index);
        self.len += 1;
        Handle { index, generation: self.nodes[index].generation }
    }

    fn unlink(&mut self, i: usize) -> T {
        let (prev, next) = (self.nodes[i].prev, self.nodes[i].next);
        match prev { Some(p) => self.nodes[p].next = next, None => self.head = next }
        match next { Some(n) => self.nodes[n].prev = prev, None => self.tail = prev }
        let node = &mut self.nodes[i];
        let v = node.value.take().unwrap();
        node.prev = None; node.next = None;
        node.generation += 1;                                                       // every old handle to this slot is now stale
        self.free.push(i);
        self.len -= 1;
        v
    }

    fn remove(&mut self, h: Handle) -> Option<T> { let i = self.index_of(h)?; Some(self.unlink(i)) }
    fn pop_front(&mut self) -> Option<T> { let h = self.head?; Some(self.unlink(h)) }

    fn move_to_back(&mut self, h: Handle) -> bool {
        let Some(i) = self.index_of(h) else { return false };
        if self.tail == Some(i) { return true; }
        let (prev, next) = (self.nodes[i].prev, self.nodes[i].next);
        match prev { Some(p) => self.nodes[p].next = next, None => self.head = next }
        if let Some(n) = next { self.nodes[n].prev = prev }
        self.nodes[i].prev = self.tail; self.nodes[i].next = None;                 // relink at the tail WITHOUT freeing: the handle stays valid
        if let Some(t) = self.tail { self.nodes[t].next = Some(i) }
        self.tail = Some(i);
        true
    }

    fn to_vec(&self) -> Vec<&T> {
        let mut out = vec![]; let mut at = self.head;
        while let Some(i) = at { out.push(self.nodes[i].value.as_ref().unwrap()); at = self.nodes[i].next; }
        out
    }
}

#[test]
fn handles_move_remove_and_go_stale() {
    let mut l = IndexList::new();
    let a = l.push_back("a");
    let b = l.push_back("b");
    let c = l.push_back("c");
    assert!(l.move_to_back(a));                                      // O(1): a moves behind c, and its handle still works
    assert_eq!(l.to_vec(), vec![&"b", &"c", &"a"]);
    assert_eq!(l.remove(c), Some("c"));                              // remove from the middle by handle
    assert_eq!(l.remove(c), None);                                   // the handle is stale now
    let d = l.push_back("d");                                        // reuses c's slot...
    assert_eq!(d.index, c.index);
    assert_eq!(l.remove(c), None);                                   // ...and the OLD handle still does not match: generation differs
    assert_eq!(l.pop_front(), Some("b"));
    assert_eq!(l.len, 2);
    assert!(l.nodes.len() <= 3);                                     // the arena did not grow: freed slots are reused
}

#[test]
fn random_operations_agree_with_a_vecdeque_model() {
    use std::collections::VecDeque;
    let mut seed = 7u64;
    let mut rand = |n: usize| { seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407); ((seed >> 33) as usize) % n };
    let mut list = IndexList::new();
    let mut model: VecDeque<(Handle, u32)> = VecDeque::new();      // the model remembers handles; the list is checked against its ORDER
    for step in 0..2000u32 {
        match rand(4) {
            0 => { let h = list.push_back(step); model.push_back((h, step)); }
            1 if !model.is_empty() => { let (h, v) = model.remove(rand(model.len())).unwrap(); assert_eq!(list.remove(h), Some(v)); assert_eq!(list.remove(h), None); }
            2 if !model.is_empty() => { let i = rand(model.len()); let e = model.remove(i).unwrap(); assert!(list.move_to_back(e.0)); model.push_back(e); }
            _ if !model.is_empty() => { let (_, v) = model.pop_front().unwrap(); assert_eq!(list.pop_front(), Some(v)); }
            _ => {}
        }
        let got: Vec<u32> = list.to_vec().into_iter().copied().collect();
        let want: Vec<u32> = model.iter().map(|&(_, v)| v).collect();
        assert_eq!(got, want, "step {step}");
        assert_eq!(list.len, model.len());
    }
}
```

### In the exercises

- **1c-01 (IndexList):** the code above is the whole stage: `push_back` (Part 1), `pop_front` (Part 2, `unlink` and free), `remove` by handle with slot reuse (Part 3) and `move_to_back` (Part 4).
- **1c-02 (the LRU replacer):** keeps a `HashMap<FrameId, Handle>` beside an `IndexList`, so `pin` is `remove(handle)` and `unpin` is `push_back`.
- **1e (ARC):** the same list type, four times, with page-to-handle maps for the ghost lists.

### Where it is used

- **Game engines and ECS** (`slotmap`, `generational-arena`, `bevy_ecs` entities): the generation is how a reference to a destroyed entity is detected.
- **Compilers**: AST and IR nodes stored in a `Vec` and referenced by index (rustc's `IndexVec`, LLVM's value numbering).
- **Caches**: the LRU list behind most caches (`lru` crate, Caffeine, Linux's page-cache LRU lists) is an intrusive list with O(1) unlink, which this is without `unsafe`.
- **Graphs**: `petgraph` stores nodes and edges as indices into vectors, for the same reason.
