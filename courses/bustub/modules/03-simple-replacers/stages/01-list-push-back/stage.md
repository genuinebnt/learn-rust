**Where this fits.** A buffer pool needs to answer "which page was used least recently?" and to **move a page to the back of the line** in constant time. C++ uses `std::list` and keeps an iterator to each element. Safe Rust has no such iterators, so this module builds the structure by hand: a doubly linked list whose nodes live in a `Vec` and point at each other by **index**.

## The task

`IndexList<T>` in `src/common/index_list.rs` has its fields given (a `Vec` of nodes with `prev`/`next` indices, `head`, `tail`, a free list, a length). The shape is a suggestion; the tests only use the public methods, so you may change the internals. Implement `push_back(value) -> Handle`: add the value after the current tail (or as the only element of an empty list), count it, and return a `Handle` the caller can keep. `len`, `is_empty`, `get`, `front` and `iter` are given so the tests can look inside.

## Tests

- A new list is empty; three pushes give `len() == 3` and `iter()` in push order, `front()` is the first.
- Each push returns a handle that `get` resolves to that element; handles are distinct. Non-`Clone` values work. A thousand pushes keep their order.

## Syntax and methods

```rust
self.nodes.push(Node { value: Some(value), prev: self.tail, next: None, generation: 0 });   // Vec::push; struct literal
let index = self.nodes.len() - 1;
match self.tail {                       // Option<usize>: Some(t) = the old tail
    Some(t) => self.nodes[t].next = Some(index),
    None => self.head = Some(index),
}
Handle { index, generation }            // the struct is defined for you; its fields are private to this module
```

## Notes

**Why indices?** A node that points to its neighbours with references (`&mut Node`) would make the list borrow itself: two `&mut` into the same structure at once, which the borrow checker rejects. `Rc<RefCell<Node>>` works but costs a heap allocation and a refcount per node. Indices into one `Vec` sidestep both: the `Vec` owns everything, and "pointers" are plain `usize`s. This arena pattern recurs in compilers, ECS game engines, and graph code.

**The generation.** A handle is `(index, generation)`. When a node is freed its generation increases, so a handle to a removed element can never be mistaken for whatever lives in that slot later. (The next stages use it.)

## In BusTub

```cpp
std::list<frame_id_t> lru_list_;                                       // the order
std::unordered_map<frame_id_t, std::list<frame_id_t>::iterator> pos_;  // a handle to each element, kept by the replacer
lru_list_.push_back(frame_id);  pos_[frame_id] = std::prev(lru_list_.end());
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `struct node { struct node *prev, *next; T value; };` allocated with `malloc` | `struct Node<T> { prev: Option<usize>, next: Option<usize>, value: Option<T> }` in a `Vec` |
| `std::list<T>`: stable iterators, `splice`, O(1) erase by iterator | no equivalent in std: `LinkedList` has no handles or splice; build it with indices |
| a raw pointer can dangle after `free`: use-after-free | a stale index is detected by the generation |
| the Linux kernel's intrusive `list_head` embedded in the object | an arena where the node *is* the slot |
| `nullptr` for "no neighbour" | `Option<usize>` (`None`) |

**Port rule:** C/C++ linked structures with back-pointers (lists, trees with parent links, graphs) become **arenas + indices** in safe Rust. If you also need O(1) lookup of "where is X", add a `HashMap<Key, Handle>` beside it (stage 5).

## Learn more
- *Learning Rust With Entirely Too Many Linked Lists*: [the book](https://rust-unofficial.github.io/too-many-lists/) (why linked lists are hard in Rust, and the options)
- Niko Matsakis, [Modeling graphs in Rust using vector indices](https://smallcultfollowing.com/babysteps/blog/2015/04/06/modeling-graphs-in-rust-using-vector-indices/) · crates [`slotmap`](https://docs.rs/slotmap) and [`generational-arena`](https://docs.rs/generational-arena) (the production versions of this idea)
- [`LinkedList`](https://doc.rust-lang.org/std/collections/struct.LinkedList.html) in std, and its [source](https://github.com/rust-lang/rust/blob/master/library/alloc/src/collections/linked_list.rs) · C++ [`std::list`](https://en.cppreference.com/w/cpp/container/list)
