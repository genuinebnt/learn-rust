One worker is correct and slow; several workers on one shared queue are fast and wrong, because two requests for the **same page** can run in the wrong order (a read before the write it should see). This stage builds the compromise: a scheduler that routes each request to a worker chosen by its page id, so requests for one page keep their order while requests for different pages run in parallel.

It is the smallest example of a design idea you will use again: **parallelism across keys, order within a key**.

**Where this fits.** One worker runs one request at a time. A real disk (an SSD) can serve many requests at once. More workers help, but they can't be allowed to reorder two requests for the *same page*.

## The task

In `src/storage/disk/disk_scheduler.rs`, `ShardedDiskScheduler` (a second scheduler, same request type, same `execute`):
- `new(disk, workers)`: one queue and one worker thread per worker (`workers` ≥ 1: panic with a message containing "at least one worker" for 0);
- `schedule(requests)`: send each request to the queue of its page's shard, `page_id mod workers`;
- `Drop`: stop and join every worker, after they finish what is queued.

## Tests

- 10 write/read pairs on one page, interleaved with other work: each read sees the write before it. 30 pages, each written and read back, on 3 workers.
- Eight 40 ms writes on four different pages take well under the 320 ms one worker needs (the workers overlap). Dropping with 40 queued writes: all 40 happen; every worker has ended. One worker works like `DiskScheduler`.

## Syntax and methods

```rust
request.page_id.0.rem_euclid(n as i32) as usize     // always 0..n, even for negative ids (% would give a negative remainder)
self.queues[shard].put(Some(request));
for worker in self.workers.drain(..) { let _ = worker.join(); }   // drain(..) moves every handle out of the Vec in place
```

## Notes

The invariant is *per-page FIFO*. Requests for the same page always take the same queue, so they run in the order scheduled; requests for different pages may run in any order and in parallel. This is how real systems keep a file system's or database's ordering guarantees while still using the device's parallelism. The buffer pool never has two requests for the same page in flight in conflicting ways except through this ordering, so it needs nothing more.

## In BusTub

BusTub's scheduler has exactly one worker. The leaderboard (extra credit) asks students to make disk access parallel; this stage is one way to do it.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `page_id % n` with a negative `page_id` is negative in C/C++ (truncating division): an out-of-bounds index | `rem_euclid` (always non-negative); or use unsigned ids |
| `std::vector<std::thread>`; `for (auto &t : workers) t.join();` | `Vec<JoinHandle<()>>`; `for w in workers.drain(..) { w.join() }` |
| `std::vector<Channel<...>>` needs `Channel` to be movable (it holds a mutex: it isn't), so people use `unique_ptr<Channel>` | `Vec<Arc<Channel<..>>>`: the `Arc` is shared with the worker anyway |
| thread-per-shard routing by hash (`std::hash<page_id_t>`) | same idea; `hash % n` or `% n` of the id |

**Port rule:** `%` on signed integers is a remainder with the dividend's sign in C/C++ *and* in Rust; Rust's `rem_euclid` is what you wanted. Checked at the type level it'd be `u32` ids.

## Learn more
- [`i32::rem_euclid`](https://doc.rust-lang.org/std/primitive.i32.html#method.rem_euclid) · [`Vec::drain`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.drain)
- [I/O scheduling](https://en.wikipedia.org/wiki/I/O_scheduling) · [`threadpool`](https://docs.rs/threadpool) and [`rayon`](https://docs.rs/rayon): what ready-made pools look like

## Performance

Routing is one `rem_euclid` and one queue push per request: O(1). With `N` workers the best-case throughput is `N` times one worker's, reached only when requests spread evenly over pages. A hot page keeps one worker busy while the others idle: the speed-up is bounded by the busiest shard (a form of Amdahl's law), and a workload that hammers one page gains nothing.

Costs to weigh: `N` threads and `N` queues of memory and context switches, and the underlying disk object must tolerate `N` concurrent calls (the in-memory disks serialise on their own lock, which caps the gain at 1 for them).

**Measure it.** Schedule 200 000 writes to distinct pages with 1, 2, 4 and 8 workers over a disk that does a short `sleep` per I/O (to model latency) and plot requests per second; then repeat with every write going to the same page and watch the speed-up vanish. Print the per-shard counts to see the balance.

## Hints

### Which operation has to stay ordered, exactly?

Only requests for the **same page** need an order relative to each other; a write to page 3 and a read of page 8 are independent. So "same page, same worker, FIFO queue" is sufficient and needs no locks between workers. Write the invariant down before coding: *for any page, requests run in the order `schedule` received them.*

### Negative page ids and the remainder

`page_id % n` in Rust (and C) has the sign of the dividend: `-1 % 4 == -1`, an out-of-range shard. `rem_euclid` always returns `0..n`. Decide what an invalid page id should do at all (BusTub treats `-1` as "none"; the scheduler should probably never see it) and make the choice explicit, not accidental.

### One stop signal per worker

Each worker waits on its own queue, so shutdown must `put(None)` into **every** queue and then join every worker. Sending one sentinel to a shared structure and joining N workers hangs N-1 of them. Check the symmetry: the number of queues, spawned threads, sentinels and joins must all be equal, and a test with `workers = 1` and with `workers = 8` should both shut down promptly.
