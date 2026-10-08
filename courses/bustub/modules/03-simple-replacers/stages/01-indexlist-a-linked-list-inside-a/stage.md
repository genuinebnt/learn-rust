This stage has 4 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · IndexList::push_back: a linked list inside a Vec

**Where this fits.** A buffer pool needs to answer "which page was used least recently?" and to **move a page to the back of the line** in constant time. C++ uses `std::list` and keeps an iterator to each element. Safe Rust has no such iterators, so this module builds the structure by hand: a doubly linked list whose nodes live in a `Vec` and point at each other by **index**.

### The task

`IndexList<T>` in `src/common/index_list.rs` has its fields given (a `Vec` of nodes with `prev`/`next` indices, `head`, `tail`, a free list, a length). The shape is a suggestion; the tests only use the public methods, so you may change the internals. Implement `push_back(value) -> Handle`: add the value after the current tail (or as the only element of an empty list), count it, and return a `Handle` the caller can keep. `len`, `is_empty`, `get`, `front` and `iter` are given so the tests can look inside.

### Tests

- A new list is empty; three pushes give `len() == 3` and `iter()` in push order, `front()` is the first.
- Each push returns a handle that `get` resolves to that element; handles are distinct. Non-`Clone` values work. A thousand pushes keep their order.

### Syntax and methods

```rust
self.nodes.push(Node { value: Some(value), prev: self.tail, next: None, generation: 0 });   // Vec::push; struct literal
let index = self.nodes.len() - 1;
match self.tail {                       // Option<usize>: Some(t) = the old tail
    Some(t) => self.nodes[t].next = Some(index),
    None => self.head = Some(index),
}
Handle { index, generation }            // the struct is defined for you; its fields are private to this module
```

### Notes

**Why indices?** A node that points to its neighbours with references (`&mut Node`) would make the list borrow itself: two `&mut` into the same structure at once, which the borrow checker rejects. `Rc<RefCell<Node>>` works but costs a heap allocation and a refcount per node. Indices into one `Vec` sidestep both: the `Vec` owns everything, and "pointers" are plain `usize`s. This arena pattern recurs in compilers, ECS game engines, and graph code.

**The generation.** A handle is `(index, generation)`. When a node is freed its generation increases, so a handle to a removed element can never be mistaken for whatever lives in that slot later. (The next stages use it.)

### In BusTub

```cpp
std::list<frame_id_t> lru_list_;                                       // the order
std::unordered_map<frame_id_t, std::list<frame_id_t>::iterator> pos_;  // a handle to each element, kept by the replacer
lru_list_.push_back(frame_id);  pos_[frame_id] = std::prev(lru_list_.end());
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `struct node { struct node *prev, *next; T value; };` allocated with `malloc` | `struct Node<T> { prev: Option<usize>, next: Option<usize>, value: Option<T> }` in a `Vec` |
| `std::list<T>`: stable iterators, `splice`, O(1) erase by iterator | no equivalent in std: `LinkedList` has no handles or splice; build it with indices |
| a raw pointer can dangle after `free`: use-after-free | a stale index is detected by the generation |
| the Linux kernel's intrusive `list_head` embedded in the object | an arena where the node *is* the slot |
| `nullptr` for "no neighbour" | `Option<usize>` (`None`) |

**Port rule:** C/C++ linked structures with back-pointers (lists, trees with parent links, graphs) become **arenas + indices** in safe Rust. If you also need O(1) lookup of "where is X", add a `HashMap<Key, Handle>` beside it (stage 5).

### Learn more
- *Learning Rust With Entirely Too Many Linked Lists*: [the book](https://rust-unofficial.github.io/too-many-lists/) (why linked lists are hard in Rust, and the options)
- Niko Matsakis, [Modeling graphs in Rust using vector indices](https://smallcultfollowing.com/babysteps/blog/2015/04/06/modeling-graphs-in-rust-using-vector-indices/) · crates [`slotmap`](https://docs.rs/slotmap) and [`generational-arena`](https://docs.rs/generational-arena) (the production versions of this idea)
- [`LinkedList`](https://doc.rust-lang.org/std/collections/struct.LinkedList.html) in std, and its [source](https://github.com/rust-lang/rust/blob/master/library/alloc/src/collections/linked_list.rs) · C++ [`std::list`](https://en.cppreference.com/w/cpp/container/list)

## Part 2 · IndexList::pop_front: unlink and free a node

**Where this fits.** Evicting the least recently used frame means taking the oldest element off the front.

### The task

In `src/common/index_list.rs`:
- `unlink(index)`: take the node at `index` out of the list: join its neighbours (or move `head`/`tail` if it was at an end), take its value, **bump its generation**, put its index on the free list, decrease `len`, return the value;
- `pop_front()`: unlink the head, if there is one.

### Tests

- Pops come out oldest first; `len` and `front` follow. Popping an empty list (also after emptying it) is `None`.
- Pushing after popping everything works. The handle of a popped element is stale (`get` says `None`).
- A queue model: 2000 random pushes and pops agree with a `VecDeque`.

### Syntax and methods

```rust
let (prev, next) = (self.nodes[index].prev, self.nodes[index].next);   // Option<usize> is Copy
match prev { Some(p) => self.nodes[p].next = next, None => self.head = next }
let value = self.nodes[index].value.take();                              // Option::take: leaves None behind
self.free.push(index);
let head = self.head?;                                                   // `?` on an Option returns None from the function
```

### Notes

Unlinking is the same four steps for a head, a middle node and a tail, if you treat "no neighbour" as "the list's own head/tail". Writing it as two separate cases (head? tail?) is where most bugs live. And note the order: read `prev`/`next` *before* you clear them.

### In BusTub

```cpp
lru_list_.pop_front();  pos_.erase(frame_id);       // std::list does the unlinking for you
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `node->prev->next = node->next; node->next->prev = node->prev; free(node);` (and crash on the ends: `prev` or `next` is `NULL`) | the `match` on `Option<usize>` handles the ends |
| `list.erase(it)` returns the next iterator; the erased iterator is invalidated (UB to use) | `unlink` bumps the generation: using the old handle returns `None` |
| `std::move(*it)` before `erase` to get the value out | `Option::take` |
| `list.front()` on an empty list is undefined behaviour | `front()` returns `Option<&T>` |

### Learn more
- [`Option::take`](https://doc.rust-lang.org/std/option/enum.Option.html#method.take) · the `?` operator on `Option`: [The Rust Book](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#a-shortcut-for-propagating-errors-the--operator)
- *Too Many Linked Lists*, [a bad but safe deque](https://rust-unofficial.github.io/too-many-lists/sixth.html)

## Part 3 · IndexList::remove: by handle, and reuse freed slots

**Where this fits.** Pinning a frame takes it out of the middle of the line.

### The task

In `src/common/index_list.rs`:
- `remove(handle)`: if the handle still names a live element (`index_of` checks index, generation and that the slot is occupied), unlink it and return the value; otherwise `None`;
- `push_back`: **reuse a freed slot** (from the free list) before growing the `Vec`. A reused node keeps its bumped generation, so handles issued before the reuse stay stale.

### Tests

- Remove from the head, middle and tail; the list stays linked. Removing twice gives `None`.
- After `remove(a)` and a new push (which takes `a`'s slot), `get(a)` is `None`, `remove(a)` is `None`, and the new element is untouched.
- 1000 push-then-remove rounds don't break anything; a model test of 3000 random pushes and removes agrees with a `Vec`.

### Syntax and methods

```rust
let index = self.index_of(handle)?;        // given: Option<usize>, None for a stale or foreign handle
Some(self.unlink(index))
if let Some(free) = self.free.pop() { node.generation = self.nodes[free].generation; self.nodes[free] = node; }
```

### Notes

This is the **ABA problem** in miniature: a handle that names slot 4, then slot 4 is freed and reused for something else; the old handle now points at the wrong element. A generation turns "same index" into "same index *and* same lifetime". Real arenas (`slotmap`, `generational-arena`) do exactly this; C++ programs usually have the bug.

### In BusTub

```cpp
auto it = pos_.find(frame_id);
if (it != pos_.end()) { lru_list_.erase(it->second); pos_.erase(it); }   // O(1): an iterator is a handle
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| a dangling iterator/pointer after `erase`: undefined behaviour, often "works" until it doesn't | stale handle → `None` |
| free list threaded through the freed nodes themselves (`struct free_node { struct free_node *next; }`) | `Vec<usize>` of free indices (a separate stack) |
| `malloc`/`free` per node | one `Vec`, grown rarely; nodes are recycled |
| generation counters are what `slotmap`, entity-component systems and Vulkan handles use | `generation: u32` per node |

**Port rule:** any C/C++ API that returns a "pointer into a container" and says "valid until the element is erased" becomes a handle that is *checked* when used.

### Learn more
- [The ABA problem](https://en.wikipedia.org/wiki/ABA_problem) · [`slotmap`](https://docs.rs/slotmap)
- C++ [`std::list::erase`](https://en.cppreference.com/w/cpp/container/list/erase) · [`Vec::swap_remove`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.swap_remove) (the other way to remove from an arena)

## Part 4 · IndexList::move_to_back

**Where this fits.** "Most recently used" means moving an element to the back each time it is touched. The ARC replacer will do it constantly.

### The task

Implement `move_to_back(handle) -> bool` in `src/common/index_list.rs`: if the handle is live, relink its node after the tail **without freeing it** (its handle must stay valid) and return `true`; if it is already the tail, change nothing and return `true`; for a stale handle return `false`.

### Tests

- Head, a middle element and the tail each move correctly (`[1,2,3,4]` → `[2,3,4,1]`, `[1,3,4,2]`, unchanged). A one-element list is fine.
- The handle still works afterwards (`get`, `remove`). A stale handle gives `false` and changes nothing.
- 2000 random moves over 50 elements agree with a `VecDeque` model; popping the whole list afterwards visits all 50 (the links are intact).

### Syntax and methods

```rust
let Some(index) = self.index_of(handle) else { return false };   // let-else
if self.tail == Some(index) { return true; }                     // Option<usize> compares with ==
```

### Notes

Moving is *detach, then attach after the tail*: the same neighbour-joining as `unlink` (without the free-list and generation bookkeeping), then the same linking as `push_back`. Reuse by copying the shapes; resist rewriting it as `remove` + `push_back`, which would give the element a new handle and force every caller to update its map.

### In BusTub

```cpp
lru_list_.splice(lru_list_.end(), lru_list_, it->second);   // O(1) move of one node to the end, iterator stays valid
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::list::splice(pos, other, it)`: relinks one node, no allocation, iterators stay valid | `move_to_back`: relink by index, handle stays valid |
| `std::rotate`, `std::move_backward` on a vector: O(n) | `Vec::remove` + `push`: O(n); `VecDeque::rotate_*` also O(n) |
| doubly linked list manipulation with raw pointers: four pointer writes, easy to get one wrong | the same four writes, on indices, and a model test to catch the wrong one |

**Port rule:** `splice` is the reason BusTub's replacers use `std::list`. If you see `splice`, you need an O(1) relink: an index list (or `slotmap` + manual links).

### Learn more
- C++ [`std::list::splice`](https://en.cppreference.com/w/cpp/container/list/splice) · [`VecDeque`](https://doc.rust-lang.org/std/collections/struct.VecDeque.html) (what to use when you don't need handles)
