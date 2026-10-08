---
title: Sharding work by key: parallelism that keeps per-page order
summary: Why one worker is correct but slow, why N unordered workers are fast but wrong, and how routing by page id gives both: per-key FIFO and cross-key parallelism.
minutes: 8
---
One disk worker is **correct**: requests run in the order they were scheduled, so a write to page 7 followed by a read of page 7 reads the new data. It is also **one thread's worth of I/O**. Add more workers on one shared queue and requests overtake each other: the read can run before the write. The way out is not a smarter queue; it is a smarter *assignment*.

## The rule: same key, same worker

Send every request for page `p` to worker `p mod N`. Each worker has its own FIFO queue.

```rust
pub fn schedule(&self, requests: Vec<DiskRequest>) {
    for request in requests {
        let shard = request.page_id.0.rem_euclid(self.queues.len() as i32) as usize;   // never negative
        self.queues[shard].put(Some(request));
    }
}
```

Two requests for the *same* page always land in the *same* queue, and a queue is served in order, so they cannot overtake each other. Requests for *different* pages may land in different queues and run at the same time. That is exactly the guarantee a database needs from its I/O layer: **order per page, concurrency across pages.**

```svg
caption: Requests are routed by page id modulo 3. The two requests for page 7 go to the same queue and stay in order; requests for other pages run on other workers at the same time.
<svg viewBox="0 0 760 250" role="img" aria-label="Six requests routed by page id modulo three to three queues, each with its own worker">
<defs><marker id="sh-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<text class="dim sm" x="20" y="22">schedule: w7, r7, w3, w4, r3, w5</text>
<rect class="hot" x="20" y="70" width="110" height="80" rx="4"/><text class="mid t-a" x="75" y="104">route</text><text class="mid dim sm" x="75" y="124">page_id mod 3</text>
<path class="ln" d="M130 90 H250" marker-end="url(#sh-a)"/><path class="ln" d="M130 130 C190 130 190 170 250 170" marker-end="url(#sh-a)"/><path class="ln" d="M130 110 C190 110 190 130 250 130" marker-end="url(#sh-a)"/>
<rect class="box" x="254" y="70" width="270" height="34" rx="3"/><text class="fg sm" x="266" y="92">queue 0: w3, r3          (3 mod 3 = 0)</text>
<rect class="blue" x="254" y="114" width="270" height="34" rx="3"/><text class="t-b sm" x="266" y="136">queue 1: w7, r7, w4     (7, 4 mod 3 = 1)</text>
<rect class="box" x="254" y="158" width="270" height="34" rx="3"/><text class="fg sm" x="266" y="180">queue 2: w5                (5 mod 3 = 2)</text>
<path class="ln" d="M524 87 H570" marker-end="url(#sh-a)"/><path class="ln" d="M524 131 H570" marker-end="url(#sh-a)"/><path class="ln" d="M524 175 H570" marker-end="url(#sh-a)"/>
<rect class="live" x="574" y="70" width="160" height="34" rx="3"/><text class="mid t-g sm" x="654" y="92">worker 0</text>
<rect class="live" x="574" y="114" width="160" height="34" rx="3"/><text class="mid t-g sm" x="654" y="136">worker 1</text>
<rect class="live" x="574" y="158" width="160" height="34" rx="3"/><text class="mid t-g sm" x="654" y="180">worker 2</text>
<text class="t-b sm" x="266" y="214">w7 always runs before r7: same queue, FIFO</text>
<text class="dim sm" x="574" y="214">workers run in parallel</text>
</svg>
```

## Details that matter

- **`rem_euclid`, not `%`.** In Rust (and C) `-7 % 4 == -3`: a negative page id (BusTub uses `-1` as invalid) would index out of range. `rem_euclid` always returns `0..N`. The C++ `page_id % n` has the same trap with signed integers.
- **A batch is routed request by request**, and the order *within* a shard is the order of `schedule`'s argument, so a caller's own sequence for one page is preserved.
- **The hash should spread the keys.** Page ids are sequential, so `p mod N` is a perfect spread here. A real system hashes the key first, or a hot page range lands on one worker.
- **Shutdown sends `None` to every queue**, then joins all the workers: one stop signal per worker, as the concept on clean shutdown describes.
- **There is still one disk underneath.** Sharding multiplies *threads*, not the device. It helps when the disk (or the `DiskIo` implementation) can serve several requests at once, as SSDs and the in-memory disks can, and does nothing for a single spinning platter.

## What it costs

| | one worker, one queue | N workers, N queues |
|---|---|---|
| ordering | global FIFO | FIFO **per shard** (so per page) |
| parallelism | none | up to N requests at once |
| load balance | n/a | depends on the key distribution: a hot page keeps one worker busy while the others idle |
| memory | one queue | N queues, N threads |
| failure | one worker to lose | losing one worker stalls 1/N of the pages |

The alternatives are worth knowing by name: a **shared queue with a lock per page** (more flexible, but every request pays a lock), and **work stealing** (idle workers take from busy queues, which breaks the per-queue order unless the stolen work is independent). Sharding is the simplest design that keeps the invariant.

> [!TIP] Measure the speed-up
> Time 100 000 writes to distinct pages with 1, 2, 4 and 8 workers against `DiskManagerUnlimitedMemory`. If the time does not fall, the disk's own lock is the bottleneck (the in-memory disks lock their whole table). That is the lesson of Amdahl's law: the serial fraction caps the speed-up, however many workers you add.
