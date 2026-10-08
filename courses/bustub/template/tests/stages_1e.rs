//! Tests for the ARC stages (1e-01 … 1e-09). A test named `s1e_05_…` belongs to stage 1e-05.
//!
//! Notation in the comments (BusTub's): `(a, fb)` is page a on frame b, `(a, _)` a ghost page, `p(a, fb)` a pinned page;
//! `[mru_ghost][mru]![mfu][mfu_ghost] p=x` with the freshest entries next to the `!`.

use bustub::buffer::arc_replacer::ArcReplacer;
use bustub::common::config::{FrameId, PageId};

fn f(n: usize) -> FrameId {
    FrameId(n)
}

fn p(n: i32) -> PageId {
    PageId(n)
}

/// Records an access and makes the frame evictable, as the buffer pool does when it unpins a page.
fn touch(r: &mut ArcReplacer, frame: usize, page: i32) {
    r.record_access(f(frame), p(page));
    r.set_evictable(f(frame), true);
}

// ---- 1e-01 · new and size ----------------------------------------------------------------------------------------------

#[test]
fn s1e_01_a_new_replacer_has_nothing_to_evict() {
    assert_eq!(ArcReplacer::new(7).size(), 0);
    assert_eq!(ArcReplacer::new(0).size(), 0);
}

// ---- 1e-02 · record_access (new pages) and set_evictable -------------------------------------------------------------------

#[test]
fn s1e_02_recorded_frames_start_out_not_evictable() {
    let mut r = ArcReplacer::new(7);
    r.record_access(f(1), p(10));
    r.record_access(f(2), p(11));
    assert_eq!(r.size(), 0);
}

#[test]
fn s1e_02_size_counts_the_evictable_frames_only() {
    // the start of BusTub's SampleTest
    let mut r = ArcReplacer::new(7);
    for n in 1..=6 {
        r.record_access(f(n), p(n as i32));
    }
    for n in 1..=5 {
        r.set_evictable(f(n), true);
    }
    r.set_evictable(f(6), false);
    assert_eq!(r.size(), 5);
}

#[test]
fn s1e_02_setting_a_flag_twice_counts_once() {
    let mut r = ArcReplacer::new(7);
    r.record_access(f(1), p(1));
    r.set_evictable(f(1), true);
    r.set_evictable(f(1), true);
    assert_eq!(r.size(), 1);
    r.set_evictable(f(1), false);
    r.set_evictable(f(1), false);
    assert_eq!(r.size(), 0);
}

#[test]
fn s1e_02_unknown_frames_are_ignored() {
    let mut r = ArcReplacer::new(7);
    r.set_evictable(f(3), true);
    r.set_evictable(f(3), false);
    assert_eq!(r.size(), 0);
}

#[test]
fn s1e_02_many_new_pages_are_fine() {
    let mut r = ArcReplacer::new(100);
    for n in 0..100 {
        touch(&mut r, n, 1000 + n as i32);
    }
    assert_eq!(r.size(), 100);
}

// ---- 1e-03 · evict ----------------------------------------------------------------------------------------------------

#[test]
fn s1e_03_the_oldest_evictable_frame_goes_first() {
    let mut r = ArcReplacer::new(7);
    for n in 1..=4 {
        touch(&mut r, n, n as i32);
    }
    assert_eq!([r.evict(), r.evict(), r.evict(), r.evict(), r.evict()], [Some(f(1)), Some(f(2)), Some(f(3)), Some(f(4)), None]);
    assert_eq!(r.size(), 0);
}

#[test]
fn s1e_03_pinned_frames_are_skipped() {
    let mut r = ArcReplacer::new(7);
    for n in 1..=3 {
        touch(&mut r, n, n as i32);
    }
    r.set_evictable(f(1), false);
    assert_eq!(r.evict(), Some(f(2)));
    assert_eq!(r.evict(), Some(f(3)));
    assert_eq!(r.evict(), None, "frame 1 is pinned");
    assert_eq!(r.size(), 0);
}

#[test]
fn s1e_03_evict_lowers_size_and_a_failed_evict_does_not() {
    let mut r = ArcReplacer::new(7);
    touch(&mut r, 1, 1);
    touch(&mut r, 2, 2);
    r.evict();
    assert_eq!(r.size(), 1);
    let mut empty = ArcReplacer::new(3);
    assert_eq!(empty.evict(), None);
}

#[test]
fn s1e_03_an_evicted_frame_can_hold_another_page() {
    let mut r = ArcReplacer::new(3);
    touch(&mut r, 1, 1);
    touch(&mut r, 2, 2);
    assert_eq!(r.evict(), Some(f(1)));
    touch(&mut r, 1, 3); // frame 1 reused for page 3
    assert_eq!(r.size(), 2);
    assert_eq!(r.evict(), Some(f(2)));
    assert_eq!(r.evict(), Some(f(1)));
}

// ---- 1e-04 · a hit on a live frame ----------------------------------------------------------------------------------------

#[test]
fn s1e_04_a_second_access_moves_a_frame_to_the_frequent_side() {
    // [][(1,f1),(2,f2),(3,f3),(4,f4)]!  then a hit on page 1:  [][(2,f2),(3,f3),(4,f4)]![(1,f1)]   p = 0, so mru is evicted first
    let mut r = ArcReplacer::new(7);
    for n in 1..=4 {
        touch(&mut r, n, n as i32);
    }
    r.record_access(f(1), p(1));
    assert_eq!([r.evict(), r.evict(), r.evict(), r.evict()], [Some(f(2)), Some(f(3)), Some(f(4)), Some(f(1))]);
}

#[test]
fn s1e_04_a_hit_in_mfu_refreshes_the_frame() {
    let mut r = ArcReplacer::new(7);
    for n in 1..=3 {
        touch(&mut r, n, n as i32);
    }
    r.record_access(f(1), p(1));
    r.record_access(f(2), p(2)); // mfu: 1, 2 (2 is fresher)
    r.record_access(f(1), p(1)); // mfu: 2, 1
    assert_eq!([r.evict(), r.evict(), r.evict()], [Some(f(3)), Some(f(2)), Some(f(1))]);
}

#[test]
fn s1e_04_a_hit_keeps_the_evictable_flag() {
    let mut r = ArcReplacer::new(7);
    touch(&mut r, 1, 1);
    r.record_access(f(1), p(1));
    assert_eq!(r.size(), 1);
    r.set_evictable(f(1), false);
    r.record_access(f(1), p(1));
    assert_eq!(r.size(), 0);
    assert_eq!(r.evict(), None);
}

#[test]
fn s1e_04_the_bustub_sample_start() {
    let mut r = ArcReplacer::new(7);
    for n in 1..=6 {
        r.record_access(f(n), p(n as i32));
    }
    for n in 1..=5 {
        r.set_evictable(f(n), true);
    }
    r.set_evictable(f(6), false);
    assert_eq!(r.size(), 5);
    r.record_access(f(1), p(1)); // frame 1 goes to mfu
    // [][(2,f2),(3,f3),(4,f4),(5,f5),p(6,f6)]![(1,f1)][] p=0: the mru side is evicted
    assert_eq!([r.evict(), r.evict(), r.evict()], [Some(f(2)), Some(f(3)), Some(f(4))]);
    assert_eq!(r.size(), 2);
}

// ---- 1e-05 · a hit on mru_ghost: the target grows ----------------------------------------------------------------------------

#[test]
fn s1e_05_a_ghost_hit_brings_the_page_back_on_the_frequent_side() {
    let mut r = ArcReplacer::new(4);
    for n in 1..=3 {
        touch(&mut r, n, n as i32);
    }
    assert_eq!(r.evict(), Some(f(1))); // [(1,_)][(2,f2),(3,f3)]!
    touch(&mut r, 1, 1); // page 1 again, on frame 1: a mru_ghost hit -> mfu.  p becomes 1
    // [][(2,f2),(3,f3)]![(1,f1)][] p=1: mru has 2 >= 1 frames, so it is evicted first
    assert_eq!([r.evict(), r.evict(), r.evict()], [Some(f(2)), Some(f(3)), Some(f(1))]);
}

#[test]
fn s1e_05_a_new_page_is_not_a_ghost_hit() {
    // BusTub: "Insert new page 7 on frame 2, this should NOT be a hit on the ghost list since we've never seen page 7"
    let mut r = ArcReplacer::new(7);
    for n in 1..=5 {
        touch(&mut r, n, n as i32);
    }
    r.record_access(f(1), p(1)); // 1 -> mfu
    for _ in 0..3 {
        r.evict(); // frames 2, 3, 4 become ghosts (pages 2, 3, 4)
    }
    touch(&mut r, 2, 7); // an unseen page on a freed frame: mru, not mfu
    // [(2,_),(3,_),(4,_)][(5,f5),(7,f2)]![(1,f1)][] p=0
    assert_eq!([r.evict(), r.evict()], [Some(f(5)), Some(f(2))], "page 7 sits in mru, behind page 5");
}

#[test]
fn s1e_05_the_target_makes_eviction_prefer_mfu_when_mru_is_small() {
    // BusTub's SampleTest, from the start to "Evict another entry, this time mru is smaller than target, mfu is victimized"
    let mut r = ArcReplacer::new(7);
    for n in 1..=6 {
        r.record_access(f(n), p(n as i32));
    }
    for n in 1..=5 {
        r.set_evictable(f(n), true);
    }
    r.set_evictable(f(6), false);
    r.record_access(f(1), p(1));
    assert_eq!([r.evict(), r.evict(), r.evict()], [Some(f(2)), Some(f(3)), Some(f(4))]);
    // [(2,_),(3,_),(4,_)][(5,f5),p(6,f6)]![(1,f1)][] p=0
    touch(&mut r, 2, 7);
    touch(&mut r, 3, 2); // ghost hit on page 2: p = 1
    // [(3,_),(4,_)][(5,f5),p(6,f6),(7,f2)]![(2,f3),(1,f1)][] p=1
    assert_eq!(r.size(), 4);
    touch(&mut r, 4, 3);
    touch(&mut r, 7, 4); // ghost hits on pages 3 and 4: p = 3
    // [][(5,f5),p(6,f6),(7,f2)]![(4,f7),(3,f4),(2,f3),(1,f1)][] p=3
    assert_eq!(r.size(), 6);
    assert_eq!(r.evict(), Some(f(5)), "mru holds 3 frames, which is >= p = 3: evict from mru");
    // [(5,_)][p(6,f6),(7,f2)]![(4,f7),(3,f4),(2,f3),(1,f1)][] p=3
    assert_eq!(r.evict(), Some(f(1)), "mru now holds 2 < 3: evict from mfu, its oldest");
}

#[test]
fn s1e_05_when_the_preferred_side_has_nothing_evictable_the_other_side_is_used() {
    let mut r = ArcReplacer::new(4);
    r.record_access(f(1), p(1)); // pinned, in mru
    touch(&mut r, 2, 2);
    r.record_access(f(2), p(2)); // frame 2 -> mfu
    // mru = [p(1)] (1 >= p = 0, so mru is preferred) but nothing there is evictable
    assert_eq!(r.evict(), Some(f(2)));
}

// ---- 1e-06 · a hit on mfu_ghost: the target shrinks ----------------------------------------------------------------------------

#[test]
fn s1e_06_a_hit_on_mfu_ghost_lowers_the_target() {
    // BusTub's SampleTest, up to "p is adjusted down by 1/1 = 1" and the eviction after it.
    let mut r = ArcReplacer::new(7);
    for n in 1..=6 {
        r.record_access(f(n), p(n as i32));
    }
    for n in 1..=5 {
        r.set_evictable(f(n), true);
    }
    r.set_evictable(f(6), false);
    r.record_access(f(1), p(1));
    r.evict();
    r.evict();
    r.evict();
    touch(&mut r, 2, 7);
    touch(&mut r, 3, 2);
    touch(&mut r, 4, 3);
    touch(&mut r, 7, 4);
    assert_eq!(r.evict(), Some(f(5)));
    assert_eq!(r.evict(), Some(f(1)));
    // [(5,_)][p(6,f6),(7,f2)]![(4,f7),(3,f4),(2,f3)][(1,_)] p=3
    touch(&mut r, 5, 1); // page 1 is on mfu_ghost: back to mfu, p = 3 - 1 = 2
    // [(5,_)][p(6,f6),(7,f2)]![(1,f5),(4,f7),(3,f4),(2,f3)][] p=2
    assert_eq!(r.size(), 5);
    assert_eq!(r.evict(), Some(f(2)), "mru holds 2 >= p = 2: evict from mru; frame 6 is pinned, so page 7 on frame 2 goes");
}

#[test]
fn s1e_06_the_target_stops_at_zero() {
    let mut r = ArcReplacer::new(3);
    touch(&mut r, 1, 1);
    r.record_access(f(1), p(1)); // mfu
    assert_eq!(r.evict(), Some(f(1))); // mru is empty (0 >= p = 0), nothing evictable there, so mfu: page 1 -> mfu_ghost
    touch(&mut r, 1, 1); // mfu_ghost hit: p = 0 - 1 saturates at 0 (and must not wrap around)
    touch(&mut r, 2, 2);
    // mru = [(2,f2)], mfu = [(1,f1)], p = 0: mru preferred
    assert_eq!(r.evict(), Some(f(2)));
}

// ---- 1e-07 · keeping the ghost lists bounded --------------------------------------------------------------------------------------

#[test]
fn s1e_07_a_new_page_pushes_out_the_oldest_mru_ghost_when_mru_and_its_ghosts_fill_c() {
    // BusTub's SampleTest2, from the start up to "Access page 1 ... Ghost page 2 should be driven out"
    let mut r = ArcReplacer::new(3);
    touch(&mut r, 1, 1);
    touch(&mut r, 2, 2);
    touch(&mut r, 3, 3);
    assert_eq!([r.evict(), r.evict(), r.evict()], [Some(f(1)), Some(f(2)), Some(f(3))]);
    // [(1,_),(2,_),(3,_)][]![][] p=0
    touch(&mut r, 3, 4); // case 4A: ghost page 1 is driven out. [(2,_),(3,_)][(4,f3)]!
    touch(&mut r, 2, 1); // page 1 is no longer a ghost, so this is a NEW page, not a ghost hit. Ghost 2 is driven out
    assert_eq!(r.size(), 2);
    // [(3,_)][(4,f3),(1,f2)]![][] p=0 -- if page 1 had been a ghost hit, it would be on mfu and p would be 1
    touch(&mut r, 1, 3); // page 3 IS still a ghost: hit. mfu: (3,f1).  p = 1
    // [][(4,f3),(1,f2)]![(3,f1)][] p=1
    assert_eq!(r.evict(), Some(f(3)), "mru holds 2 >= p = 1: evict from mru, the oldest: page 4 on frame 3");
}

#[test]
fn s1e_07_four_lists_at_twice_the_capacity_shrink_the_mfu_ghost_list() {
    // BusTub's SampleTest2 end to end: the middle of it is case 4B ("four lists total size equals 2 * capacity").
    // Test a smaller capacity
    let mut r = ArcReplacer::new(3);
    // Fill up the replacer
    r.record_access(f(1), p(1));
    r.set_evictable(f(1), true);
    r.record_access(f(2), p(2));
    r.set_evictable(f(2), true);
    r.record_access(f(3), p(3));
    r.set_evictable(f(3), true);
    assert_eq!(3, r.size());
    // Now [][(1,f1), (2,f2), (3,f3)]![][] p=0
    // Evict all pages
    assert_eq!(Some(f(1)), r.evict());
    assert_eq!(Some(f(2)), r.evict());
    assert_eq!(Some(f(3)), r.evict());
    assert_eq!(0, r.size());
    // Now [(1,_), (2,_), (3,_)][]![][] p=0

    // Insert a new page 4 with frame 3. This is case 4A
    // and ghost pages 1 should be driven out
    r.record_access(f(3), p(4));
    r.set_evictable(f(3), true);
    // Now [(2,_), (3,_)][(4,f3)]![][] p=0

    // Access page 1 on frame 2, it should NOT be a hit on
    // the ghost list. Ghost page 2 should be driven out
    r.record_access(f(2), p(1));
    r.set_evictable(f(2), true);
    assert_eq!(2, r.size());
    // Now [(3,_)][(4,f3), (1,f2)]![][] p=0

    // Access page 3 with frame 1, this should be a ghost hit,
    // page 3 is placed on mfu and target size is bumped up by 1
    r.record_access(f(1), p(3));
    r.set_evictable(f(1), true);
    // Now [][(4,f3), (1,f2)]![(3,f1)][] p=1

    // Make some more ghosts by evicting all pages again
    assert_eq!(Some(f(3)), r.evict());
    assert_eq!(Some(f(2)), r.evict());
    assert_eq!(Some(f(1)), r.evict());
    // Now [(4,_), (1,_)][]![][(3,_)] p=1

    // Let's make even more ghost to fill the list to "full"
    // Insert page 1 again so it goes to mfu side,
    // target is bumped up by 1
    r.record_access(f(1), p(1));
    r.set_evictable(f(1), true);
    // Now [(4,_)][]![(1,f1)][(3,_)] p=2

    // Insert page 4 again so it goes to mfu side,
    // target is bumped up by 1
    r.record_access(f(2), p(4));
    r.set_evictable(f(2), true);
    // Now [][]![(4,f2),(1,f1)][(3,_)] p=3

    // Now insert and evict one new page at a time
    // Insert page 5 and evict, since target size is 3,
    // should victimize page 1
    r.record_access(f(3), p(5));
    r.set_evictable(f(3), true);
    assert_eq!(Some(f(1)), r.evict());
    // Now [][(5,f3)]![(4,f2)][(1,_),(3,_)] p=3
    // Insert page 6 and evict, notice target size is 3,
    // so page 4 gets evicted
    r.record_access(f(1), p(6));
    r.set_evictable(f(1), true);
    assert_eq!(Some(f(2)), r.evict());
    // Now [][(5,f3),(6,f1)]![(4,_),(1,_),(3,_)] p=3
    // Insert page 7 and evict, notice target size is 3,
    // so page 5 gets evicted
    r.record_access(f(2), p(7));
    r.set_evictable(f(2), true);
    assert_eq!(Some(f(3)), r.evict());
    // Now [(5,_)][(6,f1),(7,f2)]![][(4,_),(1,_),(3,_)] p=3

    // Now the list is full! reaching 2*capacity
    // adjust page 5 to mfu list
    r.record_access(f(3), p(5));
    r.set_evictable(f(3), true);
    // Now [][(6,f1),(7,f2)]![(5,f3)][(4,_),(1,_),(3,_)] p=3

    // Now evict, target should be mfu
    assert_eq!(Some(f(3)), r.evict());
    // Now [][(6,f1),(7,f2)]![][(5,_),(4,_),(1,_),(3,_)] p=3

    // Now mru and mru_ghost together has
    // less than 3 records. When inserting a new page 2
    // this should be case 4B and
    // four lists total size equals 2 * capacity case,
    // So mfu ghost will be shrinked
    r.record_access(f(3), p(2));
    r.set_evictable(f(3), true);
    // Now [][(6,f1),(7,f2),(2,f3)]![][(5,_),(4,_),(1,_)] p=3

    // Evict a page 6
    assert_eq!(Some(f(1)), r.evict());
    // Now [(6,_)][(7,f2),(2,f3)]![][(5,_),(4,_),(1,_)] p=3
    // And access page 3 who was removed
    // then this is case 4A, ghost page 6 will be removed
    r.record_access(f(1), p(3));
    r.set_evictable(f(1), true);
    // Now [][(7,f2),(2,f3),(3,f1)]![][(5,_),(4,_),(1,_)] p=3

    // Finally we evict all pages and see if the order is right,
    // note that target size is 3
    assert_eq!(Some(f(2)), r.evict());
    assert_eq!(Some(f(3)), r.evict());
    assert_eq!(Some(f(1)), r.evict());
}

// ---- 1e-08 · remove -------------------------------------------------------------------------------------------------------------

#[test]
fn s1e_08_remove_drops_a_frame_and_keeps_the_order_of_the_rest() {
    let mut r = ArcReplacer::new(5);
    for n in 0..5 {
        touch(&mut r, n, 60 + n as i32);
    }
    r.remove(f(2));
    assert_eq!(r.size(), 4);
    assert_eq!([r.evict(), r.evict(), r.evict(), r.evict(), r.evict()], [Some(f(0)), Some(f(1)), Some(f(3)), Some(f(4)), None]);
}

#[test]
fn s1e_08_removing_from_mfu() {
    let mut r = ArcReplacer::new(4);
    touch(&mut r, 0, 20);
    touch(&mut r, 1, 21);
    r.record_access(f(0), p(20)); // frame 0 -> mfu
    r.remove(f(0));
    assert_eq!(r.size(), 1);
    assert_eq!(r.evict(), Some(f(1)));
    assert_eq!(r.evict(), None);
}

#[test]
fn s1e_08_remove_leaves_no_ghost() {
    // If frame 0 had been EVICTED, page 30 would be a ghost and re-accessing it would be a ghost hit (mfu, p up).
    // Removed instead, it is a new page: back in mru, behind the others.
    let mut r = ArcReplacer::new(3);
    for n in 0..3 {
        touch(&mut r, n, 30 + n as i32);
    }
    r.remove(f(0));
    touch(&mut r, 0, 30);
    assert_eq!([r.evict(), r.evict(), r.evict()], [Some(f(1)), Some(f(2)), Some(f(0))]);
}

#[test]
fn s1e_08_unknown_frames_and_double_removes_are_ignored() {
    let mut r = ArcReplacer::new(3);
    r.remove(f(0));
    touch(&mut r, 0, 40);
    r.remove(f(99));
    assert_eq!(r.size(), 1);
    r.remove(f(0));
    r.remove(f(0));
    assert_eq!(r.size(), 0);
}

#[test]
fn s1e_08_a_removed_frame_can_be_reused_for_another_page() {
    let mut r = ArcReplacer::new(3);
    touch(&mut r, 0, 50);
    r.remove(f(0));
    touch(&mut r, 0, 51);
    assert_eq!(r.size(), 1);
    assert_eq!(r.evict(), Some(f(0)));
}

#[test]
#[should_panic(expected = "not evictable")]
fn s1e_08_removing_a_pinned_frame_is_a_bug() {
    let mut r = ArcReplacer::new(3);
    r.record_access(f(0), p(1));
    r.remove(f(0));
}

// ---- 1e-09 · the module as a whole -------------------------------------------------------------------------------------------------

#[test]
fn s1e_09_the_size_always_matches_a_recount() {
    // A deterministic random workload against a slow model of just the evictable count.
    let mut x: u64 = 12345;
    let mut next = |n: usize| {
        x = x.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        ((x >> 33) as usize) % n
    };
    let mut r = ArcReplacer::new(8);
    let mut page_of = [None::<i32>; 8];
    let mut evictable = [false; 8];
    let mut next_page = 0;
    for step in 0..2000 {
        match next(4) {
            0 => {
                // access: a free frame gets a fresh page; a used frame is hit
                let frame = next(8);
                let page = page_of[frame].unwrap_or_else(|| {
                    next_page += 1;
                    next_page
                });
                r.record_access(f(frame), p(page));
                page_of[frame] = Some(page);
            }
            1 => {
                let frame = next(8);
                let flag = next(2) == 0;
                r.set_evictable(f(frame), flag);
                if page_of[frame].is_some() {
                    evictable[frame] = flag;
                }
            }
            2 => {
                if let Some(victim) = r.evict() {
                    assert!(evictable[victim.0], "step {step}: evicted a frame that was not evictable");
                    page_of[victim.0] = None;
                    evictable[victim.0] = false;
                }
            }
            _ => {
                let frame = next(8);
                if page_of[frame].is_some() && evictable[frame] {
                    r.remove(f(frame));
                    page_of[frame] = None;
                    evictable[frame] = false;
                }
            }
        }
        assert_eq!(r.size(), evictable.iter().filter(|&&e| e).count(), "step {step}");
    }
}
