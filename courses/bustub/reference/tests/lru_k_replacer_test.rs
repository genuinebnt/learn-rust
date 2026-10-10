//! Port of `test/buffer/lru_k_replacer_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database Group).

use bustub::buffer::lru_k_replacer::LruKReplacer;
use bustub::common::config::FrameId;

fn f(n: usize) -> FrameId {
    FrameId(n)
}

#[test]
fn sample_test() {
    // Initialize the replacer.
    let mut lru_replacer = LruKReplacer::new(7, 2);

    // Add six frames to the replacer. We now have frames [1, 2, 3, 4, 5]. We set frame 6 as non-evictable.
    for n in 1..=6 {
        lru_replacer.record_access(f(n));
    }
    for n in 1..=5 {
        lru_replacer.set_evictable(f(n), true);
    }
    lru_replacer.set_evictable(f(6), false);

    // The size of the replacer is the number of frames that can be evicted, _not_ the total number of frames entered.
    assert_eq!(5, lru_replacer.size());

    // Record an access for frame 1. Now frame 1 has two accesses total.
    lru_replacer.record_access(f(1));
    // All other frames now share the maximum backward k-distance. Since we use timestamps to break ties, where the first
    // to be evicted is the frame with the oldest timestamp, the order of eviction should be [2, 3, 4, 5, 1].

    // Evict three pages from the replacer.
    // To break ties, we use LRU with respect to the oldest timestamp, or the least recently used frame.
    assert_eq!(Some(f(2)), lru_replacer.evict());
    assert_eq!(Some(f(3)), lru_replacer.evict());
    assert_eq!(Some(f(4)), lru_replacer.evict());
    assert_eq!(2, lru_replacer.size());
    // Now the replacer has the frames [5, 1].

    // Insert new frames [3, 4], and update the access history for 5. Now, the ordering is [3, 1, 5, 4].
    lru_replacer.record_access(f(3));
    lru_replacer.record_access(f(4));
    lru_replacer.record_access(f(5));
    lru_replacer.record_access(f(4));
    lru_replacer.set_evictable(f(3), true);
    lru_replacer.set_evictable(f(4), true);
    assert_eq!(4, lru_replacer.size());

    // Look for a frame to evict. We expect frame 3 to be evicted next.
    assert_eq!(Some(f(3)), lru_replacer.evict());
    assert_eq!(3, lru_replacer.size());

    // Set 6 to be evictable. 6 should be evicted next since it has the maximum backward k-distance.
    lru_replacer.set_evictable(f(6), true);
    assert_eq!(4, lru_replacer.size());
    assert_eq!(Some(f(6)), lru_replacer.evict());
    assert_eq!(3, lru_replacer.size());

    // Mark frame 1 as non-evictable. We now have [5, 4].
    lru_replacer.set_evictable(f(1), false);

    // We expect frame 5 to be evicted next.
    assert_eq!(2, lru_replacer.size());
    assert_eq!(Some(f(5)), lru_replacer.evict());
    assert_eq!(1, lru_replacer.size());

    // Update the access history for frame 1 and make it evictable. Now we have [4, 1].
    lru_replacer.record_access(f(1));
    lru_replacer.record_access(f(1));
    lru_replacer.set_evictable(f(1), true);
    assert_eq!(2, lru_replacer.size());

    // Evict the last two frames.
    assert_eq!(Some(f(4)), lru_replacer.evict());
    assert_eq!(1, lru_replacer.size());
    assert_eq!(Some(f(1)), lru_replacer.evict());
    assert_eq!(0, lru_replacer.size());

    // Insert frame 1 again and mark it as non-evictable.
    lru_replacer.record_access(f(1));
    lru_replacer.set_evictable(f(1), false);
    assert_eq!(0, lru_replacer.size());

    // A failed eviction should not change the size of the replacer.
    assert_eq!(None, lru_replacer.evict());

    // Mark frame 1 as evictable again and evict it.
    lru_replacer.set_evictable(f(1), true);
    assert_eq!(1, lru_replacer.size());
    assert_eq!(Some(f(1)), lru_replacer.evict());
    assert_eq!(0, lru_replacer.size());

    // There is nothing left in the replacer, so make sure this doesn't do something strange.
    assert_eq!(None, lru_replacer.evict());
    assert_eq!(0, lru_replacer.size());

    // Make sure that setting a nonexistent frame as evictable or non-evictable doesn't do something strange.
    lru_replacer.set_evictable(f(6), false);
    lru_replacer.set_evictable(f(6), true);
}
