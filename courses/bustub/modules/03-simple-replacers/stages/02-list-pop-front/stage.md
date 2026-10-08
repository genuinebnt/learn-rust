**Where this fits.** Evicting the least recently used frame means taking the oldest element off the front.

## The task

In `src/common/index_list.rs`:
- `unlink(index)`: take the node at `index` out of the list: join its neighbours (or move `head`/`tail` if it was at an end), take its value, **bump its generation**, put its index on the free list, decrease `len`, return the value;
- `pop_front()`: unlink the head, if there is one.

## Tests

- Pops come out oldest first; `len` and `front` follow. Popping an empty list (also after emptying it) is `None`.
- Pushing after popping everything works. The handle of a popped element is stale (`get` says `None`).
- A queue model: 2000 random pushes and pops agree with a `VecDeque`.

## Syntax and methods

```rust
let (prev, next) = (self.nodes[index].prev, self.nodes[index].next);   // Option<usize> is Copy
match prev { Some(p) => self.nodes[p].next = next, None => self.head = next }
let value = self.nodes[index].value.take();                              // Option::take: leaves None behind
self.free.push(index);
let head = self.head?;                                                   // `?` on an Option returns None from the function
```

## Notes

Unlinking is the same four steps for a head, a middle node and a tail, if you treat "no neighbour" as "the list's own head/tail". Writing it as two separate cases (head? tail?) is where most bugs live. And note the order: read `prev`/`next` *before* you clear them.

## In BusTub

```cpp
lru_list_.pop_front();  pos_.erase(frame_id);       // std::list does the unlinking for you
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `node->prev->next = node->next; node->next->prev = node->prev; free(node);` (and crash on the ends: `prev` or `next` is `NULL`) | the `match` on `Option<usize>` handles the ends |
| `list.erase(it)` returns the next iterator; the erased iterator is invalidated (UB to use) | `unlink` bumps the generation: using the old handle returns `None` |
| `std::move(*it)` before `erase` to get the value out | `Option::take` |
| `list.front()` on an empty list is undefined behaviour | `front()` returns `Option<&T>` |

## Learn more
- [`Option::take`](https://doc.rust-lang.org/std/option/enum.Option.html#method.take) · the `?` operator on `Option`: [The Rust Book](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#a-shortcut-for-propagating-errors-the--operator)
- *Too Many Linked Lists*, [a bad but safe deque](https://rust-unofficial.github.io/too-many-lists/sixth.html)
