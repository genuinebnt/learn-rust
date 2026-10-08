---
title: Reader-writer latches: many readers or one writer
summary: What an RwLock promises and does not, why read-then-write upgrades deadlock, and where BusTub's page latches and the B+ tree's latch crabbing come from.
minutes: 8
---
A `Mutex` lets one thread in at a time. Most shared data is read far more often than it is written, and readers do not conflict with each other. A **reader-writer lock** (BusTub calls it a *latch*) lets any number of readers in together, or exactly one writer alone.

## The contract

| held by | a new reader | a new writer |
|---|---|---|
| nobody | gets in | gets in |
| one or more readers | gets in (*usually*) | waits until they all leave |
| a writer | waits | waits |

Rust's `RwLock<T>` follows it, in the same ownership-based shape as `Mutex<T>`: `lock.read()` returns a guard that derefs to `&T`, `lock.write()` returns one that derefs to `&mut T`, and dropping the guard releases the latch. The compiler therefore stops you from writing through a read guard.

```rust
pub struct ReaderWriterLatch<T> { inner: RwLock<T> }

impl<T> ReaderWriterLatch<T> {
    pub fn read(&self)  -> RwLockReadGuard<'_, T>  { self.inner.read().unwrap_or_else(PoisonError::into_inner) }
    pub fn write(&self) -> RwLockWriteGuard<'_, T> { self.inner.write().unwrap_or_else(PoisonError::into_inner) }
}
```

BusTub's `ReaderWriterLatch` has four calls (`RLock`, `RUnlock`, `WLock`, `WUnlock`) wrapped around a `std::shared_mutex`, and every code path must pair them. In Rust the pair collapses into a guard's lifetime: there is no `RUnlock` to forget.

```svg
caption: Readers overlap with each other; the writer waits for all of them and then has the latch to itself. A new reader that arrives while the writer holds it waits.
<svg viewBox="0 0 760 230" role="img" aria-label="Timelines of two readers, a writer and a late reader on one latch">
<text class="big" x="20" y="48">reader A</text><text class="big" x="20" y="92">reader B</text><text class="big" x="20" y="136">writer</text><text class="big" x="20" y="180">reader C</text>
<rect class="live" x="130" y="30" width="190" height="26" rx="4"/><text class="mid t-g sm" x="225" y="48">read guard</text>
<rect class="live" x="190" y="74" width="190" height="26" rx="4"/><text class="mid t-g sm" x="285" y="92">read guard</text>
<rect class="never" x="230" y="118" width="150" height="26" rx="4"/><text class="mid dim sm" x="305" y="136">waits for A and B</text>
<rect class="bad" x="380" y="118" width="150" height="26" rx="4"/><text class="mid t-r sm" x="455" y="136">write guard</text>
<rect class="never" x="440" y="162" width="90" height="26" rx="4"/><text class="mid dim sm" x="485" y="180">waits</text>
<rect class="live" x="530" y="162" width="140" height="26" rx="4"/><text class="mid t-g sm" x="600" y="180">read guard</text>
<line class="ln dash" x1="380" y1="24" x2="380" y2="196" style="stroke:var(--warn)"/><text class="t-w sm" x="386" y="22">A and B release</text>
<text class="dim sm" x="130" y="218">time &#8594;</text>
</svg>
```

## What the lock does *not* promise

- **Fairness.** If readers keep arriving, a waiting writer can starve; if a waiting writer blocks *new* readers, readers can stall behind it. The standard library documents that the policy depends on the operating system and that no particular one is guaranteed. Do not write code whose correctness depends on who goes first.
- **Upgrades.** There is no "turn my read latch into a write latch". Releasing the read latch and then taking the write latch leaves a gap in which another writer may have changed the data, so everything you read earlier must be re-checked. Trying to take the write latch *while holding* the read latch deadlocks: you are waiting for readers to leave, and you are one of them.
- **Recursive reads.** A thread that holds a read latch and takes another read latch on the same lock may deadlock if a writer is waiting in between (the writer blocks the second read, the first read blocks the writer). Take a lock once, pass the guard down.

## Poisoning, again

If a thread panics holding the *write* guard, the lock is poisoned, as with a mutex. A panic holding a read guard does not poison it (the data cannot have been changed). The reference `ReaderWriterLatch` uses `unwrap_or_else(PoisonError::into_inner)` to ignore the poison flag: a deliberate choice for a latch whose protected data is plain bytes, made explicit in code.

## Where this goes next

A page in the buffer pool has one of these latches, and the B+ tree in module 2c walks from the root to a leaf *holding a latch on each page it passes*, releasing a parent only when the child is known to be **safe** (it cannot split or merge). That protocol is called **latch crabbing**, and it only works because latches are cheap, scoped by a guard, and acquired in a fixed order: parent before child, left before right.

| | C++ | Rust |
|---|---|---|
| the type | `std::shared_mutex` | `RwLock<T>` |
| read | `std::shared_lock l(m);` | `let g = lock.read().unwrap();` |
| write | `std::unique_lock l(m);` | `let g = lock.write().unwrap();` |
| try without blocking | `try_lock_shared()` | `try_read()` |
| protects the data | no, by convention | yes: the data is inside |
