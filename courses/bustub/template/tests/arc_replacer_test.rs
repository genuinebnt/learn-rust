//! Port of `test/buffer/arc_replacer_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database Group).
//!
//! Notation in the comments: `(a, fb)` is page a on frame b, `(a, _)` a ghost page with page id a, `p(a, fb)` a pinned page;
//! `[<-mru_ghost-][<-mru-]![-mfu->][->mfu_ghost->] p=x` shows the four lists with the freshest pages next to the `!`.

use bustub::buffer::arc_replacer::ArcReplacer;
use bustub::common::config::{FrameId, PageId};

fn f(n: usize) -> FrameId {
    FrameId(n)
}

fn p(n: i32) -> PageId {
    PageId(n)
}

#[test]
fn sample_test() {
    let mut arc_replacer = ArcReplacer::new(7);
    // Add six frames to the replacer.
    // We set frame 6 as non-evictable. These pages all go to mru list
    // We now have frames [][(1,f1), (2,f2), (3,f3), (4,f4), (5,f5), p(6,f6)]![][]
    arc_replacer.record_access(f(1), p(1));
    arc_replacer.record_access(f(2), p(2));
    arc_replacer.record_access(f(3), p(3));
    arc_replacer.record_access(f(4), p(4));
    arc_replacer.record_access(f(5), p(5));
    arc_replacer.record_access(f(6), p(6));
    arc_replacer.set_evictable(f(1), true);
    arc_replacer.set_evictable(f(2), true);
    arc_replacer.set_evictable(f(3), true);
    arc_replacer.set_evictable(f(4), true);
    arc_replacer.set_evictable(f(5), true);
    arc_replacer.set_evictable(f(6), false);

    // The size of the replacer is the number of frames that can be evicted, _not_ the total number of frames entered.
    assert_eq!(5, arc_replacer.size());
    // Record an access for frame 1. Now frame 1 goes into mfu list
    arc_replacer.record_access(f(1), p(1));
    // Now [][(2,f2), (3,f3), (4,f4), (5,f5), p(6,f6)]![(1,f1)][] p=0
    //
    // Now Evict three pages from the replacer.
    // Since target size is still 0, mru side should be evicted
    assert_eq!(Some(f(2)), arc_replacer.evict());
    assert_eq!(Some(f(3)), arc_replacer.evict());
    assert_eq!(Some(f(4)), arc_replacer.evict());
    assert_eq!(2, arc_replacer.size());
    // Now [(2,_), (3,_), (4,_)][(5,f5), p(6,f6)]![(1,f1)][] p=0

    // Insert new page 7 on frame 2, this should NOT be a hit on ghost
    // list since we've never seen page 7, this goes into mru list
    arc_replacer.record_access(f(2), p(7));
    arc_replacer.set_evictable(f(2), true);
    // Insert page 2 on frame 3, this should be a hit on mru ghost list
    // since we've just evicted page 2, this goes into mfu list
    // also target size should be bumped up by 1, since mru ghost has
    // size 3 and mfu ghost has size 0
    arc_replacer.record_access(f(3), p(2));
    arc_replacer.set_evictable(f(3), true);
    // Now [(3,_), (4,_)][(5,f5), p(6,f6), (7,f2)]![(2,f3), (1,f1)][] p=1
    assert_eq!(4, arc_replacer.size());

    // Continue to insert page 3 on frame 4 and page 4 on frame 7
    arc_replacer.record_access(f(4), p(3));
    arc_replacer.set_evictable(f(4), true);
    arc_replacer.record_access(f(7), p(4));
    arc_replacer.set_evictable(f(7), true);
    // Now [][(5,f5), p(6,f6), (7,f2)]![(4,f7), (3,f4), (2,f3), (1,f1)][] p=3
    assert_eq!(6, arc_replacer.size());

    // Evict an entry, now target size is 3, we still evict from mru
    assert_eq!(Some(f(5)), arc_replacer.evict());
    // Now [(5,_)][p(6,f6), (7,f2)]![(4,f7), (3,f4), (2,f3), (1,f1)][] p=3
    // Evict another entry, this time mru is smaller than target,
    // mfu is victimized
    assert_eq!(Some(f(1)), arc_replacer.evict());
    // Now [(5,_)][p(6,f6), (7,f2)]![(4,f7), (3,f4), (2,f3)][(1,_)] p=3

    // Make another access to page 1 on frame 5, now page 1 is back to mfu
    // with a different frame, also p is adjusted down by 1/1=1
    arc_replacer.record_access(f(5), p(1));
    arc_replacer.set_evictable(f(5), true);
    // Now [(5,_)][p(6,f6), (7,f2)]![(1,f5), (4,f7), (3,f4), (2,f3)][] p=2
    assert_eq!(5, arc_replacer.size());

    // We evict again, this time target size is 2, we evict from mru,
    // note that page 6 is pinned. Victim is page 7
    // Now [(5,_), (7,_)][p(6,f6)]![(1,f5), (4,f7), (3,f4), (2,f3)][] p=2
    assert_eq!(Some(f(2)), arc_replacer.evict());
}

#[test]
fn sample_test2() {
    // Test a smaller capacity
    let mut arc_replacer = ArcReplacer::new(3);
    // Fill up the replacer
    arc_replacer.record_access(f(1), p(1));
    arc_replacer.set_evictable(f(1), true);
    arc_replacer.record_access(f(2), p(2));
    arc_replacer.set_evictable(f(2), true);
    arc_replacer.record_access(f(3), p(3));
    arc_replacer.set_evictable(f(3), true);
    assert_eq!(3, arc_replacer.size());
    // Now [][(1,f1), (2,f2), (3,f3)]![][] p=0
    // Evict all pages
    assert_eq!(Some(f(1)), arc_replacer.evict());
    assert_eq!(Some(f(2)), arc_replacer.evict());
    assert_eq!(Some(f(3)), arc_replacer.evict());
    assert_eq!(0, arc_replacer.size());
    // Now [(1,_), (2,_), (3,_)][]![][] p=0

    // Insert a new page 4 with frame 3. This is case 4A
    // and ghost pages 1 should be driven out
    arc_replacer.record_access(f(3), p(4));
    arc_replacer.set_evictable(f(3), true);
    // Now [(2,_), (3,_)][(4,f3)]![][] p=0

    // Access page 1 on frame 2, it should NOT be a hit on
    // the ghost list. Ghost page 2 should be driven out
    arc_replacer.record_access(f(2), p(1));
    arc_replacer.set_evictable(f(2), true);
    assert_eq!(2, arc_replacer.size());
    // Now [(3,_)][(4,f3), (1,f2)]![][] p=0

    // Access page 3 with frame 1, this should be a ghost hit,
    // page 3 is placed on mfu and target size is bumped up by 1
    arc_replacer.record_access(f(1), p(3));
    arc_replacer.set_evictable(f(1), true);
    // Now [][(4,f3), (1,f2)]![(3,f1)][] p=1

    // Make some more ghosts by evicting all pages again
    assert_eq!(Some(f(3)), arc_replacer.evict());
    assert_eq!(Some(f(2)), arc_replacer.evict());
    assert_eq!(Some(f(1)), arc_replacer.evict());
    // Now [(4,_), (1,_)][]![][(3,_)] p=1

    // Let's make even more ghost to fill the list to "full"
    // Insert page 1 again so it goes to mfu side,
    // target is bumped up by 1
    arc_replacer.record_access(f(1), p(1));
    arc_replacer.set_evictable(f(1), true);
    // Now [(4,_)][]![(1,f1)][(3,_)] p=2

    // Insert page 4 again so it goes to mfu side,
    // target is bumped up by 1
    arc_replacer.record_access(f(2), p(4));
    arc_replacer.set_evictable(f(2), true);
    // Now [][]![(4,f2),(1,f1)][(3,_)] p=3

    // Now insert and evict one new page at a time
    // Insert page 5 and evict, since target size is 3,
    // should victimize page 1
    arc_replacer.record_access(f(3), p(5));
    arc_replacer.set_evictable(f(3), true);
    assert_eq!(Some(f(1)), arc_replacer.evict());
    // Now [][(5,f3)]![(4,f2)][(1,_),(3,_)] p=3
    // Insert page 6 and evict, notice target size is 3,
    // so page 4 gets evicted
    arc_replacer.record_access(f(1), p(6));
    arc_replacer.set_evictable(f(1), true);
    assert_eq!(Some(f(2)), arc_replacer.evict());
    // Now [][(5,f3),(6,f1)]![(4,_),(1,_),(3,_)] p=3
    // Insert page 7 and evict, notice target size is 3,
    // so page 5 gets evicted
    arc_replacer.record_access(f(2), p(7));
    arc_replacer.set_evictable(f(2), true);
    assert_eq!(Some(f(3)), arc_replacer.evict());
    // Now [(5,_)][(6,f1),(7,f2)]![][(4,_),(1,_),(3,_)] p=3

    // Now the list is full! reaching 2*capacity
    // adjust page 5 to mfu list
    arc_replacer.record_access(f(3), p(5));
    arc_replacer.set_evictable(f(3), true);
    // Now [][(6,f1),(7,f2)]![(5,f3)][(4,_),(1,_),(3,_)] p=3

    // Now evict, target should be mfu
    assert_eq!(Some(f(3)), arc_replacer.evict());
    // Now [][(6,f1),(7,f2)]![][(5,_),(4,_),(1,_),(3,_)] p=3

    // Now mru and mru_ghost together has
    // less than 3 records. When inserting a new page 2
    // this should be case 4B and
    // four lists total size equals 2 * capacity case,
    // So mfu ghost will be shrinked
    arc_replacer.record_access(f(3), p(2));
    arc_replacer.set_evictable(f(3), true);
    // Now [][(6,f1),(7,f2),(2,f3)]![][(5,_),(4,_),(1,_)] p=3

    // Evict a page 6
    assert_eq!(Some(f(1)), arc_replacer.evict());
    // Now [(6,_)][(7,f2),(2,f3)]![][(5,_),(4,_),(1,_)] p=3
    // And access page 3 who was removed
    // then this is case 4A, ghost page 6 will be removed
    arc_replacer.record_access(f(1), p(3));
    arc_replacer.set_evictable(f(1), true);
    // Now [][(7,f2),(2,f3),(3,f1)]![][(5,_),(4,_),(1,_)] p=3

    // Finally we evict all pages and see if the order is right,
    // note that target size is 3
    assert_eq!(Some(f(2)), arc_replacer.evict());
    assert_eq!(Some(f(3)), arc_replacer.evict());
    assert_eq!(Some(f(1)), arc_replacer.evict());
}

#[test]
fn remove_behavior_test() {
    // Scenario 1: Remove from empty replacer — should be a no-op
    {
        let mut arc_replacer = ArcReplacer::new(5);
        arc_replacer.remove(f(0));
        assert_eq!(0, arc_replacer.size());
    }

    // Scenario 2: Remove a non-existent frame_id — should be a no-op
    {
        let mut arc_replacer = ArcReplacer::new(5);
        arc_replacer.record_access(f(0), p(10));
        arc_replacer.set_evictable(f(0), true);
        assert_eq!(1, arc_replacer.size());
        arc_replacer.remove(f(99)); // never inserted
        assert_eq!(1, arc_replacer.size());
    }

    // Scenario 3: Remove an evictable frame from MRU
    {
        let mut arc_replacer = ArcReplacer::new(5);
        arc_replacer.record_access(f(0), p(10));
        arc_replacer.set_evictable(f(0), true);
        arc_replacer.record_access(f(1), p(11));
        arc_replacer.set_evictable(f(1), true);
        arc_replacer.record_access(f(2), p(12));
        arc_replacer.set_evictable(f(2), true);
        // State: [][(10,f0),(11,f1),(12,f2)]![][] p=0
        assert_eq!(3, arc_replacer.size());

        arc_replacer.remove(f(1)); // remove middle frame from MRU
        assert_eq!(2, arc_replacer.size());

        // Evict remaining: should be f0 then f2 (oldest to newest in MRU)
        assert_eq!(Some(f(0)), arc_replacer.evict());
        assert_eq!(Some(f(2)), arc_replacer.evict());
        assert_eq!(None, arc_replacer.evict());
    }

    // Scenario 4: Remove an evictable frame from MFU
    {
        let mut arc_replacer = ArcReplacer::new(4);
        arc_replacer.record_access(f(0), p(20));
        arc_replacer.set_evictable(f(0), true);
        arc_replacer.record_access(f(1), p(21));
        arc_replacer.set_evictable(f(1), true);
        // Move frame 0 to MFU by accessing again
        arc_replacer.record_access(f(0), p(20));
        // State: [][(21,f1)]![(20,f0)][] p=0
        assert_eq!(2, arc_replacer.size());

        arc_replacer.remove(f(0)); // remove from MFU
        assert_eq!(1, arc_replacer.size());

        // Only frame 1 remains
        assert_eq!(Some(f(1)), arc_replacer.evict());
        assert_eq!(None, arc_replacer.evict());
    }

    // Scenario 5: Remove does NOT create ghost entries
    // If Evict were used instead of Remove, page_id 30 would go into a ghost list.
    // On re-access, it would be a ghost hit → placed in MFU and target size adjusted.
    // With Remove, no ghost is created → re-access goes to MRU as a fresh entry.
    {
        let mut arc_replacer = ArcReplacer::new(3);
        arc_replacer.record_access(f(0), p(30));
        arc_replacer.set_evictable(f(0), true);
        arc_replacer.record_access(f(1), p(31));
        arc_replacer.set_evictable(f(1), true);
        arc_replacer.record_access(f(2), p(32));
        arc_replacer.set_evictable(f(2), true);
        // State: [][(30,f0),(31,f1),(32,f2)]![][] p=0

        // Remove frame 0 (page 30) — no ghost created
        arc_replacer.remove(f(0));
        assert_eq!(2, arc_replacer.size());
        // State: [][(31,f1),(32,f2)]![][] p=0

        // Re-add frame 0 with the same page_id 30.
        // Since no ghost exists, this is Case IV (miss all lists) → goes to MRU.
        arc_replacer.record_access(f(0), p(30));
        arc_replacer.set_evictable(f(0), true);
        // State: [][(31,f1),(32,f2),(30,f0)]![][] p=0

        // Evict order from MRU (target=0, all in MRU): f1, f2, f0
        assert_eq!(Some(f(1)), arc_replacer.evict());
        assert_eq!(Some(f(2)), arc_replacer.evict());
        assert_eq!(Some(f(0)), arc_replacer.evict());
    }

    // Scenario 6: Double remove (same frame_id twice)
    {
        let mut arc_replacer = ArcReplacer::new(3);
        arc_replacer.record_access(f(0), p(40));
        arc_replacer.set_evictable(f(0), true);
        assert_eq!(1, arc_replacer.size());

        arc_replacer.remove(f(0));
        assert_eq!(0, arc_replacer.size());

        // Second remove is a no-op (frame no longer in alive_map_)
        arc_replacer.remove(f(0));
        assert_eq!(0, arc_replacer.size());
    }

    // Scenario 7: Remove then re-insert same frame with a different page_id
    {
        let mut arc_replacer = ArcReplacer::new(3);
        arc_replacer.record_access(f(0), p(50));
        arc_replacer.set_evictable(f(0), true);

        arc_replacer.remove(f(0));
        assert_eq!(0, arc_replacer.size());

        // Re-use frame 0 with a new page
        arc_replacer.record_access(f(0), p(51));
        arc_replacer.set_evictable(f(0), true);
        assert_eq!(1, arc_replacer.size());
        assert_eq!(Some(f(0)), arc_replacer.evict());
    }

    // Scenario 8: Remove middle frame preserves eviction order of remaining frames
    {
        let mut arc_replacer = ArcReplacer::new(5);
        for i in 0..5 {
            arc_replacer.record_access(f(i), p(60 + i as i32));
            arc_replacer.set_evictable(f(i), true);
        }
        // MRU: [(60,f0),(61,f1),(62,f2),(63,f3),(64,f4)]
        arc_replacer.remove(f(2));
        assert_eq!(4, arc_replacer.size());

        // Evict order: f0, f1, f3, f4 (frame 2 skipped)
        assert_eq!(Some(f(0)), arc_replacer.evict());
        assert_eq!(Some(f(1)), arc_replacer.evict());
        assert_eq!(Some(f(3)), arc_replacer.evict());
        assert_eq!(Some(f(4)), arc_replacer.evict());
        assert_eq!(None, arc_replacer.evict());
    }

    // Scenario 9: Remove all frames one by one
    {
        let mut arc_replacer = ArcReplacer::new(5);
        for i in 0..5 {
            arc_replacer.record_access(f(i), p(80 + i as i32));
            arc_replacer.set_evictable(f(i), true);
        }
        assert_eq!(5, arc_replacer.size());

        for i in 0..5 {
            arc_replacer.remove(f(i));
        }
        assert_eq!(0, arc_replacer.size());
        assert_eq!(None, arc_replacer.evict());
    }
}
