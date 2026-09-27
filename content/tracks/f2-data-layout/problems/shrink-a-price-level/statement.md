A matching engine keeps one `PriceLevel` per price on each side of the book, and a busy instrument has
thousands of them. Each level is **96 bytes**: a copy of the symbol, a `VecDeque` of order ids that
allocates as it grows, an `Option<u64>` timestamp, the side, an `active` flag. Cancels scan the queue.

Shrink `PriceLevel` to **32 bytes** with the same public API and behaviour (price-time priority,
`level`, `best`, `orders_at`, `execute`, `cancel`), and:

- once `Book::with_capacity(n)` has run, adding and cancelling orders at an **existing** level makes
  **no allocation**, as long as at most `n` orders rest;
- `cancel` is O(1) (a level may hold 100 000 orders);
- an `OrderId` stays unique: cancelling a filled or cancelled order returns `false` and touches nothing.

Timestamps are any `u64`; prices are `u32` ticks; quantities are `u64` and never 0.
