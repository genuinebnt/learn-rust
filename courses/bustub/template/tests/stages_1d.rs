//! Tests for the LRU-K stages (1d-01 … 1d-04). A test named `s1d_05_…` belongs to stage 1d-02.

use std::time::{Duration, Instant};

use bustub::buffer::lru_k_replacer::{LruKNode, LruKReplacer};
use bustub::common::config::FrameId;

fn f(n: usize) -> FrameId {
    FrameId(n)
}

/// Records one access to each frame, in order.
fn touch(r: &mut LruKReplacer, frames: &[usize]) {
    for &n in frames {
        r.record_access(f(n));
    }
}

fn evictable(r: &mut LruKReplacer, frames: &[usize]) {
    for &n in frames {
        r.set_evictable(f(n), true);
    }
}

// ---- 1d-01 · LruKNode::record -------------------------------------------------------------------------------------------

#[test]
fn s1d_01_a_new_node_has_no_history() {
    let node = LruKNode::new(f(1), 2);
    assert_eq!(node.first_timestamp(), None);
    assert_eq!(node.frame_id(), f(1));
    assert!(!node.is_evictable());
}

#[test]
fn s1d_01_the_oldest_access_is_the_first() {
    let mut node = LruKNode::new(f(1), 3);
    node.record(10);
    assert_eq!(node.first_timestamp(), Some(10));
    node.record(11);
    node.record(12);
    assert_eq!(node.first_timestamp(), Some(10));
}

#[test]
fn s1d_01_only_the_k_most_recent_accesses_are_kept() {
    let mut node = LruKNode::new(f(1), 3);
    for t in 1..=5 {
        node.record(t);
    }
    assert_eq!(node.first_timestamp(), Some(3), "after 1,2,3,4,5 with k = 3 the history is 3,4,5");
    node.record(6);
    assert_eq!(node.first_timestamp(), Some(4));
}

#[test]
fn s1d_01_k_equal_to_one_keeps_only_the_latest() {
    let mut node = LruKNode::new(f(9), 1);
    node.record(5);
    node.record(8);
    assert_eq!(node.first_timestamp(), Some(8));
}

#[test]
fn s1d_01_a_long_run_keeps_a_bounded_history() {
    let mut node = LruKNode::new(f(0), 4);
    for t in 0..10_000 {
        node.record(t);
    }
    assert_eq!(node.first_timestamp(), Some(9_996));
}

// ---- 1d-01 · kth_timestamp ---------------------------------------------------------------------------------------------

#[test]
fn s1d_02_fewer_than_k_accesses_means_infinite_distance() {
    let mut node = LruKNode::new(f(1), 3);
    assert_eq!(node.kth_timestamp(), None);
    node.record(1);
    node.record(2);
    assert_eq!(node.kth_timestamp(), None);
}

#[test]
fn s1d_02_with_k_accesses_it_is_the_oldest_of_them() {
    let mut node = LruKNode::new(f(1), 3);
    for t in [4, 7, 9] {
        node.record(t);
    }
    assert_eq!(node.kth_timestamp(), Some(4));
}

#[test]
fn s1d_02_it_moves_forward_as_old_accesses_fall_out() {
    let mut node = LruKNode::new(f(1), 2);
    node.record(1);
    node.record(5);
    assert_eq!(node.kth_timestamp(), Some(1));
    node.record(9);
    assert_eq!(node.kth_timestamp(), Some(5));
}

#[test]
fn s1d_02_k_equal_to_one_is_the_latest_access() {
    let mut node = LruKNode::new(f(1), 1);
    assert_eq!(node.kth_timestamp(), None);
    node.record(3);
    assert_eq!(node.kth_timestamp(), Some(3));
    node.record(8);
    assert_eq!(node.kth_timestamp(), Some(8));
}

// ---- 1d-01 · new, record_access, size ----------------------------------------------------------------------------------

#[test]
fn s1d_03_a_new_replacer_has_nothing_to_evict() {
    assert_eq!(LruKReplacer::new(7, 2).size(), 0);
}

#[test]
fn s1d_03_recorded_frames_start_out_not_evictable() {
    let mut r = LruKReplacer::new(7, 2);
    touch(&mut r, &[1, 2, 3, 1]);
    assert_eq!(r.size(), 0);
}

#[test]
fn s1d_03_every_frame_below_the_limit_is_accepted() {
    let mut r = LruKReplacer::new(5, 2);
    touch(&mut r, &[0, 1, 2, 3, 4]);
}

#[test]
#[should_panic(expected = "out of range")]
fn s1d_03_a_frame_at_the_limit_is_a_bug() {
    let mut r = LruKReplacer::new(5, 2);
    r.record_access(f(5));
}

#[test]
#[should_panic(expected = "out of range")]
fn s1d_03_a_frame_far_beyond_the_limit_is_a_bug() {
    let mut r = LruKReplacer::new(5, 2);
    r.record_access(f(1000));
}

#[test]
#[should_panic(expected = "at least 1")]
fn s1d_03_k_of_zero_is_a_bug() {
    let _ = LruKReplacer::new(5, 0);
}

// ---- 1d-02 · set_evictable ---------------------------------------------------------------------------------------------

#[test]
fn s1d_04_size_counts_the_evictable_frames_only() {
    let mut r = LruKReplacer::new(7, 2);
    touch(&mut r, &[1, 2, 3, 4, 5, 6]);
    evictable(&mut r, &[1, 2, 3, 4, 5]);
    r.set_evictable(f(6), false);
    assert_eq!(r.size(), 5);
}

#[test]
fn s1d_04_setting_the_same_value_twice_counts_once() {
    let mut r = LruKReplacer::new(7, 2);
    touch(&mut r, &[1]);
    r.set_evictable(f(1), true);
    r.set_evictable(f(1), true);
    assert_eq!(r.size(), 1);
    r.set_evictable(f(1), false);
    r.set_evictable(f(1), false);
    assert_eq!(r.size(), 0);
}

#[test]
fn s1d_04_toggling_goes_up_and_down() {
    let mut r = LruKReplacer::new(7, 2);
    touch(&mut r, &[1, 2]);
    r.set_evictable(f(1), true);
    r.set_evictable(f(2), true);
    assert_eq!(r.size(), 2);
    r.set_evictable(f(1), false);
    assert_eq!(r.size(), 1);
    r.set_evictable(f(1), true);
    assert_eq!(r.size(), 2);
}

#[test]
fn s1d_04_a_frame_that_was_never_recorded_is_ignored() {
    let mut r = LruKReplacer::new(7, 2);
    r.set_evictable(f(6), true);
    r.set_evictable(f(6), false);
    assert_eq!(r.size(), 0);
}

#[test]
fn s1d_04_further_accesses_keep_the_evictable_flag() {
    let mut r = LruKReplacer::new(7, 2);
    touch(&mut r, &[1]);
    r.set_evictable(f(1), true);
    touch(&mut r, &[1, 1]);
    assert_eq!(r.size(), 1);
}

// ---- 1d-02 · evict: frames with fewer than k accesses --------------------------------------------------------------------

#[test]
fn s1d_05_with_one_access_each_the_oldest_goes_first() {
    let mut r = LruKReplacer::new(10, 2);
    touch(&mut r, &[3, 1, 2]);
    evictable(&mut r, &[1, 2, 3]);
    assert_eq!([r.evict(), r.evict(), r.evict(), r.evict()], [Some(f(3)), Some(f(1)), Some(f(2)), None]);
}

#[test]
fn s1d_05_not_evictable_frames_are_skipped() {
    let mut r = LruKReplacer::new(10, 2);
    touch(&mut r, &[1, 2, 3]);
    evictable(&mut r, &[2, 3]);
    assert_eq!(r.evict(), Some(f(2)));
    assert_eq!(r.evict(), Some(f(3)));
    assert_eq!(r.evict(), None, "frame 1 was never made evictable");
    assert_eq!(r.size(), 0);
}

#[test]
fn s1d_05_evict_lowers_size_and_a_failed_evict_does_not() {
    let mut r = LruKReplacer::new(10, 2);
    touch(&mut r, &[1, 2]);
    evictable(&mut r, &[1, 2]);
    assert_eq!(r.size(), 2);
    r.evict();
    assert_eq!(r.size(), 1);
    let mut empty = LruKReplacer::new(3, 2);
    assert_eq!(empty.evict(), None);
    assert_eq!(empty.size(), 0);
}

#[test]
fn s1d_05_an_evicted_frame_starts_over() {
    let mut r = LruKReplacer::new(10, 2);
    touch(&mut r, &[1, 2]);
    evictable(&mut r, &[1, 2]);
    assert_eq!(r.evict(), Some(f(1)));
    touch(&mut r, &[1]); // frame 1 comes back: a NEW frame, not evictable until it is marked
    assert_eq!(r.size(), 1);
    r.set_evictable(f(1), true);
    assert_eq!(r.size(), 2);
    assert_eq!(r.evict(), Some(f(2)), "frame 1's old history is gone: its only access is now newer than frame 2's");
    assert_eq!(r.evict(), Some(f(1)));
}

#[test]
fn s1d_05_an_access_does_not_move_a_frame_that_stays_below_k() {
    // k = 3: frames 1 and 2 have 1 and 2 accesses. Both are "infinite"; the one whose FIRST access is older goes first.
    let mut r = LruKReplacer::new(10, 3);
    touch(&mut r, &[1, 2, 2]);
    evictable(&mut r, &[1, 2]);
    assert_eq!(r.evict(), Some(f(1)));
    assert_eq!(r.evict(), Some(f(2)));
}

#[test]
fn s1d_05_ties_break_on_the_first_access_not_the_latest() {
    let mut r = LruKReplacer::new(10, 3);
    touch(&mut r, &[1, 2, 1]); // 1: accesses at times 0 and 2; 2: access at time 1
    evictable(&mut r, &[1, 2]);
    assert_eq!(r.evict(), Some(f(1)), "frame 1's FIRST access (time 0) is older than frame 2's (time 1)");
}

// ---- 1d-02 · evict: the k-th access counts ------------------------------------------------------------------------------

#[test]
fn s1d_06_frames_below_k_go_before_frames_with_k_accesses() {
    let mut r = LruKReplacer::new(10, 2);
    touch(&mut r, &[1, 1, 2]); // 1 has two accesses, 2 has one
    evictable(&mut r, &[1, 2]);
    assert_eq!(r.evict(), Some(f(2)));
    assert_eq!(r.evict(), Some(f(1)));
}

#[test]
fn s1d_06_among_full_histories_the_oldest_kth_access_goes_first() {
    let mut r = LruKReplacer::new(10, 2);
    // times: 0:a 1:b 2:a 3:b 4:b 5:a ...   a's last two accesses: 2,5 -> kth = 2;  b's: 3,4 -> kth = 3
    touch(&mut r, &[1, 2, 1, 2, 2, 1]);
    evictable(&mut r, &[1, 2]);
    assert_eq!(r.evict(), Some(f(1)), "frame 1's 2nd most recent access (time 2) is older than frame 2's (time 3)");
    assert_eq!(r.evict(), Some(f(2)));
}

#[test]
fn s1d_06_recent_bursts_do_not_hide_an_old_kth_access() {
    let mut r = LruKReplacer::new(10, 2);
    touch(&mut r, &[1, 2, 2, 2, 1]); // frame 1: times 0, 4 -> kth 0.   frame 2: times 1,2,3 -> history 2,3 -> kth 2
    evictable(&mut r, &[1, 2]);
    assert_eq!(r.evict(), Some(f(1)), "LRU would keep frame 1 (touched last); LRU-2 evicts it");
}

#[test]
fn s1d_06_the_bustub_walkthrough() {
    // The LRUKReplacerTest sample, step by step (k = 2).
    let mut r = LruKReplacer::new(7, 2);
    touch(&mut r, &[1, 2, 3, 4, 5, 6]);
    evictable(&mut r, &[1, 2, 3, 4, 5]);
    assert_eq!(r.size(), 5);
    touch(&mut r, &[1]); // frame 1 now has two accesses
    assert_eq!([r.evict(), r.evict(), r.evict()], [Some(f(2)), Some(f(3)), Some(f(4))]);
    assert_eq!(r.size(), 2);
    touch(&mut r, &[3, 4, 5, 4]);
    evictable(&mut r, &[3, 4]);
    assert_eq!(r.size(), 4);
    assert_eq!(r.evict(), Some(f(3)));
    r.set_evictable(f(6), true);
    assert_eq!(r.evict(), Some(f(6)), "frame 6 has one access: infinite distance");
}

#[test]
fn s1d_06_a_model_agrees_on_random_workloads() {
    // A slow, obvious reference: keep every access time, compute distances from scratch.
    struct Rng(u64);
    impl Rng {
        fn next(&mut self, n: usize) -> usize {
            self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
            ((self.0 >> 33) as usize) % n
        }
    }
    for seed in 0..30 {
        let k = 1 + seed as usize % 3;
        let mut rng = Rng(seed + 1);
        let mut r = LruKReplacer::new(12, k);
        let mut times: Vec<Vec<usize>> = vec![Vec::new(); 12];
        let mut ev = [false; 12];
        let mut now = 0;
        for step in 0..300 {
            match rng.next(4) {
                0 | 1 => {
                    let n = rng.next(12);
                    r.record_access(f(n));
                    times[n].push(now);
                    now += 1;
                }
                2 => {
                    let n = rng.next(12);
                    let flag = rng.next(2) == 0;
                    r.set_evictable(f(n), flag);
                    if !times[n].is_empty() {
                        ev[n] = flag;
                    }
                }
                _ => {
                    let want = (0..12)
                        .filter(|&n| ev[n])
                        .min_by_key(|&n| {
                            let t = &times[n];
                            if t.len() < k { (0, t[0]) } else { (1, t[t.len() - k]) }
                        });
                    let got = r.evict();
                    assert_eq!(got, want.map(f), "seed {seed} step {step}");
                    if let Some(n) = want {
                        times[n].clear();
                        ev[n] = false;
                    }
                }
            }
            assert_eq!(r.size(), ev.iter().filter(|&&e| e).count(), "seed {seed} step {step}");
        }
    }
}

// ---- 1d-02 · remove ----------------------------------------------------------------------------------------------------

#[test]
fn s1d_07_remove_drops_an_evictable_frame() {
    let mut r = LruKReplacer::new(10, 2);
    touch(&mut r, &[1, 2, 3]);
    evictable(&mut r, &[1, 2, 3]);
    r.remove(f(2));
    assert_eq!(r.size(), 2);
    assert_eq!([r.evict(), r.evict(), r.evict()], [Some(f(1)), Some(f(3)), None]);
}

#[test]
fn s1d_07_removing_an_unknown_frame_does_nothing() {
    let mut r = LruKReplacer::new(10, 2);
    r.remove(f(4));
    touch(&mut r, &[1]);
    r.set_evictable(f(1), true);
    r.remove(f(9));
    assert_eq!(r.size(), 1);
}

#[test]
#[should_panic(expected = "not evictable")]
fn s1d_07_removing_a_frame_that_is_not_evictable_is_a_bug() {
    let mut r = LruKReplacer::new(10, 2);
    touch(&mut r, &[1]);
    r.remove(f(1));
}

#[test]
fn s1d_07_a_removed_frame_has_no_history_left() {
    let mut r = LruKReplacer::new(10, 2);
    touch(&mut r, &[1, 1, 2, 2]);
    evictable(&mut r, &[1, 2]);
    r.remove(f(1));
    touch(&mut r, &[1]); // starts fresh: one access, infinite distance, not evictable yet
    r.set_evictable(f(1), true);
    assert_eq!(r.evict(), Some(f(1)), "a single access is infinite distance, so frame 1 now goes before frame 2");
}

#[test]
fn s1d_07_removing_every_frame_leaves_an_empty_replacer() {
    let mut r = LruKReplacer::new(10, 2);
    touch(&mut r, &[0, 1, 2, 3]);
    evictable(&mut r, &[0, 1, 2, 3]);
    for n in 0..4 {
        r.remove(f(n));
    }
    assert_eq!(r.size(), 0);
    assert_eq!(r.evict(), None);
}

// ---- 1d-03 · evict in O(log n) -----------------------------------------------------------------------------------------

#[test]
fn s1d_08_a_hundred_thousand_frames_evict_quickly_and_in_order() {
    let n = 100_000;
    let mut r = LruKReplacer::new(n, 2);
    let start = Instant::now();
    for i in 0..n {
        r.record_access(f(i));
    }
    for i in 0..n {
        r.set_evictable(f(i), true);
    }
    for i in 0..n {
        assert_eq!(r.evict(), Some(f(i)), "frames have one access each: oldest first");
    }
    assert_eq!(r.evict(), None);
    assert!(start.elapsed() < Duration::from_secs(5), "took {:?}: evict must not scan every frame", start.elapsed());
}

#[test]
fn s1d_08_accesses_to_evictable_frames_reorder_them() {
    let n = 50_000;
    let mut r = LruKReplacer::new(n, 2);
    let start = Instant::now();
    for i in 0..n {
        r.record_access(f(i));
        r.set_evictable(f(i), true);
    }
    for i in 0..n {
        r.record_access(f(i)); // a second access for everyone: now they have finite distances, ordered by their first access
    }
    for i in 0..n {
        assert_eq!(r.evict(), Some(f(i)));
    }
    assert!(start.elapsed() < Duration::from_secs(5), "took {:?}", start.elapsed());
}

#[test]
fn s1d_08_marking_frames_not_evictable_and_back_keeps_the_order() {
    let mut r = LruKReplacer::new(100, 2);
    for i in 0..100 {
        r.record_access(f(i));
        r.set_evictable(f(i), true);
    }
    for i in (0..100).step_by(2) {
        r.set_evictable(f(i), false);
    }
    for i in (0..100).step_by(2) {
        r.set_evictable(f(i), true);
    }
    for i in 0..100 {
        assert_eq!(r.evict(), Some(f(i)));
    }
}

/// A deliberately naive LRU-K to compare against: the same rules, one linear scan per eviction.
struct NaiveLruK {
    k: usize,
    now: usize,
    /// frame -> (the last k access times, oldest first; evictable)
    frames: std::collections::HashMap<usize, (Vec<usize>, bool)>,
}

impl NaiveLruK {
    fn new(k: usize) -> NaiveLruK {
        NaiveLruK { k, now: 0, frames: Default::default() }
    }
    fn record(&mut self, frame: usize) {
        let k = self.k;
        let entry = self.frames.entry(frame).or_insert((Vec::new(), false));
        entry.0.push(self.now);
        if entry.0.len() > k {
            entry.0.remove(0);
        }
        self.now += 1;
    }
    fn size(&self) -> usize {
        self.frames.values().filter(|(_, e)| *e).count()
    }
    fn evict(&mut self) -> Option<usize> {
        let k = self.k;
        let victim = self
            .frames
            .iter()
            .filter(|(_, (_, e))| *e)
            .min_by_key(|(&fr, (h, _))| if h.len() < k { (0, h[0], fr) } else { (1, h[0], fr) })
            .map(|(&fr, _)| fr)?;
        self.frames.remove(&victim);
        Some(victim)
    }
}

struct Lcg8(u64);
impl Lcg8 {
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        self.0 >> 33
    }
}

#[test]
fn s1d_08_it_agrees_with_a_naive_scan_on_random_operations() {
    // The fast version must pick the same victim as a linear scan over the same history, for several values of k.
    for k in [1usize, 2, 3, 5] {
        let mut fast = LruKReplacer::new(48, k);
        let mut slow = NaiveLruK::new(k);
        let mut rng = Lcg8(1000 + k as u64);
        for step in 0..4000 {
            let frame = (rng.next() % 48) as usize;
            match rng.next() % 10 {
                0..=4 => {
                    fast.record_access(f(frame));
                    slow.record(frame);
                }
                5..=7 => {
                    let on = rng.next() % 2 == 0;
                    fast.set_evictable(f(frame), on);
                    if let Some(e) = slow.frames.get_mut(&frame) {
                        e.1 = on;
                    }
                }
                _ => {
                    assert_eq!(fast.evict().map(|x| x.0), slow.evict(), "k={k}, step {step}: the two disagree about the victim");
                }
            }
            assert_eq!(fast.size(), slow.size(), "k={k}, step {step}: the evictable counts differ");
        }
    }
}

#[test]
fn s1d_08_a_removed_frame_starts_over_at_the_back_of_the_order() {
    let mut r = LruKReplacer::new(10, 2);
    for n in 0..4 {
        r.record_access(f(n));
        r.set_evictable(f(n), true);
    }
    r.remove(f(0));
    r.record_access(f(0)); // forgotten, then seen again: a brand-new single access, newer than 1, 2 and 3
    r.set_evictable(f(0), true);
    let order: Vec<usize> = std::iter::from_fn(|| r.evict().map(|x| x.0)).collect();
    assert_eq!(order, vec![1, 2, 3, 0]);
}

#[test]
fn s1d_08_frames_with_k_accesses_are_ordered_by_their_kth_most_recent() {
    let mut r = LruKReplacer::new(10, 2);
    // access times: t0:f0 t1:f1 t2:f0 t3:f1 t4:f2 t5:f2 -> f0 has {0,2}, f1 has {1,3}, f2 has {4,5}
    for n in [0, 1, 0, 1, 2, 2] {
        r.record_access(f(n));
    }
    for n in 0..3 {
        r.set_evictable(f(n), true);
    }
    r.record_access(f(0)); // t6: f0's last two are now {2, 6}: its 2nd most recent access moved from t0 to t2
    // 2nd most recent access times: f1 at t1, f0 at t2, f2 at t4: the largest backward distance goes first
    assert_eq!(r.evict(), Some(f(1)));
    assert_eq!(r.evict(), Some(f(0)));
    assert_eq!(r.evict(), Some(f(2)));
}

// ---- 1d-04 · the module as a whole -------------------------------------------------------------------------------------

#[test]
fn s1d_09_scans_do_not_flush_the_hot_pages() {
    // A tiny buffer pool of 4 frames driven by the replacer: 2 hot pages touched repeatedly, then a scan of 20 cold pages.
    // LRU-2 keeps the hot pages (they have two accesses); plain LRU would not.
    let mut r = LruKReplacer::new(4, 2);
    let mut resident: Vec<Option<usize>> = vec![None; 4]; // frame -> page
    let mut access = |r: &mut LruKReplacer, page: usize| -> bool {
        if let Some(frame) = resident.iter().position(|p| *p == Some(page)) {
            r.record_access(f(frame));
            return true;
        }
        let frame = match resident.iter().position(|p| p.is_none()) {
            Some(free) => free,
            None => r.evict().expect("a victim").0,
        };
        resident[frame] = Some(page);
        r.record_access(f(frame));
        r.set_evictable(f(frame), true);
        false
    };
    for _ in 0..3 {
        access(&mut r, 100);
        access(&mut r, 101);
    }
    for page in 0..20 {
        access(&mut r, page);
    }
    assert!(access(&mut r, 100), "hot page 100 survived the scan");
    assert!(access(&mut r, 101), "hot page 101 survived the scan");
}
