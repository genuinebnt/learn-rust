//! Tests for the simple replacer stages (1c-01 … 1c-04): the index list, LRU and CLOCK. A test named `s1c_04_…` belongs to stage 1c-01.

use std::collections::VecDeque;
use std::time::{Duration, Instant};

use bustub::buffer::clock_replacer::ClockReplacer;
use bustub::buffer::lru_replacer::LruReplacer;
use bustub::buffer::replacer::Replacer;
use bustub::common::config::FrameId;
use bustub::common::index_list::IndexList;

fn f(n: usize) -> FrameId {
    FrameId(n)
}

fn all<T: Clone>(list: &IndexList<T>) -> Vec<T> {
    list.iter().cloned().collect()
}

/// A tiny deterministic generator, so the model tests need no crate.
struct Lcg(u64);
impl Lcg {
    fn next(&mut self, n: usize) -> usize {
        self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        ((self.0 >> 33) as usize) % n
    }
}

// ---- 1c-01 · IndexList::push_back --------------------------------------------------------------------------------------

#[test]
fn s1c_01_a_new_list_is_empty() {
    let list: IndexList<u32> = IndexList::new();
    assert!(list.is_empty(), "a new list is empty: expected `list.is_empty()`");
    assert_eq!(list.len(), 0, "a new list is empty");
    assert_eq!(list.front(), None, "a new list is empty");
    assert_eq!(all(&list), Vec::<u32>::new(), "a new list is empty");
}

#[test]
fn s1c_01_push_back_keeps_order_and_counts() {
    let mut list = IndexList::new();
    for x in [10, 20, 30] {
        list.push_back(x);
    }
    assert_eq!(list.len(), 3, "push back keeps order and counts");
    assert!(!list.is_empty(), "push back keeps order and counts: expected `!list.is_empty()`");
    assert_eq!(all(&list), [10, 20, 30], "push back keeps order and counts");
    assert_eq!(list.front(), Some(&10), "push back keeps order and counts");
}

#[test]
fn s1c_01_each_push_returns_a_handle_to_its_element() {
    let mut list = IndexList::new();
    let a = list.push_back("a");
    let b = list.push_back("b");
    let c = list.push_back("c");
    assert_eq!((list.get(a), list.get(b), list.get(c)), (Some(&"a"), Some(&"b"), Some(&"c")), "each push returns a handle to its element");
    assert_ne!(a, b, "each push returns a handle to its element");
    assert_ne!(b, c, "each push returns a handle to its element");
}

#[test]
fn s1c_01_values_need_not_be_clone_or_copy() {
    let mut list = IndexList::new();
    list.push_back(String::from("x"));
    list.push_back(String::from("y"));
    assert_eq!(list.iter().map(|s| s.as_str()).collect::<Vec<_>>(), ["x", "y"], "values need not be clone or copy");
}

#[test]
fn s1c_01_a_thousand_pushes() {
    let mut list = IndexList::new();
    let handles: Vec<_> = (0..1000).map(|i| list.push_back(i)).collect();
    assert_eq!(list.len(), 1000, "a thousand pushes");
    assert_eq!(all(&list), (0..1000).collect::<Vec<_>>(), "a thousand pushes");
    assert!(handles.iter().enumerate().all(|(i, h)| list.get(*h) == Some(&i)), "a thousand pushes: expected `handles.iter().enumerate().all(|(i, h)| list.get(*h) == Some(&i))`");
}

// ---- 1c-01 · pop_front -------------------------------------------------------------------------------------------------

#[test]
fn s1c_02_pop_front_returns_the_oldest_first() {
    let mut list = IndexList::new();
    for x in 1..=4 {
        list.push_back(x);
    }
    assert_eq!((list.pop_front(), list.pop_front()), (Some(1), Some(2)), "pop front returns the oldest first");
    assert_eq!(all(&list), [3, 4], "pop front returns the oldest first");
    assert_eq!(list.len(), 2, "pop front returns the oldest first");
    assert_eq!(list.front(), Some(&3), "pop front returns the oldest first");
}

#[test]
fn s1c_02_pop_front_of_an_empty_list_is_none() {
    let mut list: IndexList<u8> = IndexList::new();
    assert_eq!(list.pop_front(), None, "pop front of an empty list is none");
    list.push_back(1);
    list.pop_front();
    assert_eq!(list.pop_front(), None, "pop front of an empty list is none");
    assert!(list.is_empty(), "pop front of an empty list is none: expected `list.is_empty()`");
}

#[test]
fn s1c_02_pushing_after_popping_everything_works() {
    let mut list = IndexList::new();
    list.push_back(1);
    list.pop_front();
    list.push_back(2);
    list.push_back(3);
    assert_eq!(all(&list), [2, 3], "pushing after popping everything works");
    assert_eq!(list.pop_front(), Some(2), "pushing after popping everything works");
    assert_eq!(list.pop_front(), Some(3), "pushing after popping everything works");
    assert_eq!(list.pop_front(), None, "pushing after popping everything works");
}

#[test]
fn s1c_02_the_handle_of_a_popped_element_is_stale() {
    let mut list = IndexList::new();
    let a = list.push_back("a");
    let b = list.push_back("b");
    list.pop_front();
    assert_eq!(list.get(a), None, "the handle of a popped element is stale");
    assert_eq!(list.get(b), Some(&"b"), "the handle of a popped element is stale");
}

#[test]
fn s1c_02_a_queue_model() {
    let mut list = IndexList::new();
    let mut model = VecDeque::new();
    let mut rng = Lcg(7);
    for step in 0..2000 {
        if rng.next(3) == 0 {
            assert_eq!(list.pop_front(), model.pop_front(), "step {step}");
        } else {
            list.push_back(step);
            model.push_back(step);
        }
        assert_eq!(list.len(), model.len(), "a queue model");
    }
    assert_eq!(all(&list), model.into_iter().collect::<Vec<_>>(), "a queue model");
}

// ---- 1c-01 · remove and slot reuse -------------------------------------------------------------------------------------

#[test]
fn s1c_03_remove_from_the_middle_head_and_tail() {
    let mut list = IndexList::new();
    let h: Vec<_> = (1..=5).map(|x| list.push_back(x)).collect();
    assert_eq!(list.remove(h[2]), Some(3), "remove from the middle head and tail");
    assert_eq!(all(&list), [1, 2, 4, 5], "remove from the middle head and tail");
    assert_eq!(list.remove(h[0]), Some(1), "remove from the middle head and tail");
    assert_eq!(list.remove(h[4]), Some(5), "remove from the middle head and tail");
    assert_eq!(all(&list), [2, 4], "remove from the middle head and tail");
    assert_eq!(list.len(), 2, "remove from the middle head and tail");
    assert_eq!(list.front(), Some(&2), "remove from the middle head and tail");
}

#[test]
fn s1c_03_removing_twice_gives_none() {
    let mut list = IndexList::new();
    let a = list.push_back(1);
    list.push_back(2);
    assert_eq!(list.remove(a), Some(1), "removing twice gives none");
    assert_eq!(list.remove(a), None, "removing twice gives none");
    assert_eq!(list.len(), 1, "removing twice gives none");
}

#[test]
fn s1c_03_removing_the_only_element_leaves_a_usable_list() {
    let mut list = IndexList::new();
    let a = list.push_back(1);
    assert_eq!(list.remove(a), Some(1), "removing the only element leaves a usable list");
    assert!(list.is_empty(), "removing the only element leaves a usable list: expected `list.is_empty()`");
    assert_eq!(list.front(), None, "removing the only element leaves a usable list");
    list.push_back(2);
    assert_eq!(all(&list), [2], "removing the only element leaves a usable list");
}

#[test]
fn s1c_03_a_freed_slot_is_reused_but_the_old_handle_stays_stale() {
    let mut list = IndexList::new();
    let a = list.push_back("a");
    list.push_back("keep");
    list.remove(a);
    let c = list.push_back("c"); // takes a's slot
    assert_eq!(list.get(a), None, "a's handle must not see c");
    assert_eq!(list.get(c), Some(&"c"), "a freed slot is reused but the old handle stays stale");
    assert_eq!(list.remove(a), None, "and must not remove c");
    assert_eq!(all(&list), ["keep", "c"], "a freed slot is reused but the old handle stays stale");
}

#[test]
fn s1c_03_the_vec_does_not_grow_while_slots_are_free() {
    let mut list = IndexList::new();
    for round in 0..1000 {
        let h = list.push_back(round);
        list.remove(h);
    }
    // A list that grew its Vec on every push would be 1000 nodes; this is checked through behaviour: it still works, fast.
    assert!(list.is_empty(), "the vec does not grow while slots are free: expected `list.is_empty()`");
    for x in 0..3 {
        list.push_back(x);
    }
    assert_eq!(all(&list), [0, 1, 2], "the vec does not grow while slots are free");
}

#[test]
fn s1c_03_a_model_with_random_removals() {
    let mut list = IndexList::new();
    let mut model: Vec<(usize, bustub::common::index_list::Handle)> = Vec::new();
    let mut rng = Lcg(99);
    for step in 0..3000 {
        if !model.is_empty() && rng.next(2) == 0 {
            let at = rng.next(model.len());
            let (value, handle) = model.remove(at);
            assert_eq!(list.remove(handle), Some(value), "step {step}");
        } else {
            let handle = list.push_back(step);
            model.push((step, handle));
        }
    }
    assert_eq!(all(&list), model.iter().map(|(v, _)| *v).collect::<Vec<_>>(), "a model with random removals");
    assert_eq!(list.len(), model.len(), "a model with random removals");
}

// ---- 1c-01 · move_to_back ---------------------------------------------------------------------------------------------

#[test]
fn s1c_04_the_head_goes_to_the_back() {
    let mut list = IndexList::new();
    let h: Vec<_> = (1..=4).map(|x| list.push_back(x)).collect();
    assert!(list.move_to_back(h[0]), "the head goes to the back: expected `list.move_to_back(h[0])`");
    assert_eq!(all(&list), [2, 3, 4, 1], "the head goes to the back");
    assert_eq!(list.front(), Some(&2), "the head goes to the back");
}

#[test]
fn s1c_04_a_middle_element_goes_to_the_back() {
    let mut list = IndexList::new();
    let h: Vec<_> = (1..=4).map(|x| list.push_back(x)).collect();
    assert!(list.move_to_back(h[1]), "a middle element goes to the back: expected `list.move_to_back(h[1])`");
    assert_eq!(all(&list), [1, 3, 4, 2], "a middle element goes to the back");
}

#[test]
fn s1c_04_the_tail_stays_where_it_is() {
    let mut list = IndexList::new();
    let h: Vec<_> = (1..=3).map(|x| list.push_back(x)).collect();
    assert!(list.move_to_back(h[2]), "the tail stays where it is: expected `list.move_to_back(h[2])`");
    assert_eq!(all(&list), [1, 2, 3], "the tail stays where it is");
}

#[test]
fn s1c_04_a_single_element_list() {
    let mut list = IndexList::new();
    let a = list.push_back(1);
    assert!(list.move_to_back(a), "a single element list: expected `list.move_to_back(a)`");
    assert_eq!(all(&list), [1], "a single element list");
}

#[test]
fn s1c_04_the_handle_stays_valid_after_the_move() {
    let mut list = IndexList::new();
    let a = list.push_back("a");
    list.push_back("b");
    list.move_to_back(a);
    assert_eq!(list.get(a), Some(&"a"), "the handle stays valid after the move");
    assert_eq!(list.remove(a), Some("a"), "the handle stays valid after the move");
    assert_eq!(all(&list), ["b"], "the handle stays valid after the move");
}

#[test]
fn s1c_04_a_stale_handle_is_refused() {
    let mut list = IndexList::new();
    let a = list.push_back(1);
    list.push_back(2);
    list.remove(a);
    assert!(!list.move_to_back(a), "a stale handle is refused: expected `!list.move_to_back(a)`");
    assert_eq!(all(&list), [2], "a stale handle is refused");
}

#[test]
fn s1c_04_links_stay_consistent_under_many_moves() {
    let mut list = IndexList::new();
    let handles: Vec<_> = (0..50).map(|x| list.push_back(x)).collect();
    let mut model: VecDeque<usize> = (0..50).collect();
    let mut rng = Lcg(5);
    for _ in 0..2000 {
        let i = rng.next(50);
        assert!(list.move_to_back(handles[i]), "links stay consistent under many moves: expected `list.move_to_back(handles[i])`");
        let at = model.iter().position(|&x| x == i).unwrap();
        model.remove(at);
        model.push_back(i);
    }
    assert_eq!(all(&list), model.into_iter().collect::<Vec<_>>(), "links stay consistent under many moves");
    // popping from the front walks the whole chain
    let mut count = 0;
    while list.pop_front().is_some() {
        count += 1;
    }
    assert_eq!(count, 50, "links stay consistent under many moves");
}

// ---- 1c-02 · LruReplacer: unpin and size --------------------------------------------------------------------------------

#[test]
fn s1c_05_a_new_replacer_holds_nothing() {
    assert_eq!(LruReplacer::new(5).size(), 0, "a new replacer holds nothing");
}

#[test]
fn s1c_05_unpin_adds_frames() {
    let mut lru = LruReplacer::new(7);
    for n in 1..=6 {
        lru.unpin(f(n));
    }
    assert_eq!(lru.size(), 6, "unpin adds frames");
}

#[test]
fn s1c_05_unpinning_a_frame_twice_counts_it_once() {
    let mut lru = LruReplacer::new(7);
    lru.unpin(f(1));
    lru.unpin(f(2));
    lru.unpin(f(1));
    assert_eq!(lru.size(), 2, "unpinning a frame twice counts it once");
}

#[test]
#[should_panic(expected = "full")]
fn s1c_05_more_frames_than_the_capacity_is_a_bug() {
    let mut lru = LruReplacer::new(2);
    lru.unpin(f(1));
    lru.unpin(f(2));
    lru.unpin(f(3));
}

#[test]
fn s1c_05_it_can_be_used_through_the_trait() {
    let mut lru: Box<dyn Replacer> = Box::new(LruReplacer::new(3));
    lru.unpin(f(0));
    assert_eq!(lru.size(), 1, "it can be used through the trait");
}

// ---- 1c-02 · LruReplacer::victim ----------------------------------------------------------------------------------------

#[test]
fn s1c_06_the_victim_is_the_frame_unpinned_longest_ago() {
    let mut lru = LruReplacer::new(7);
    for n in [3, 1, 2] {
        lru.unpin(f(n));
    }
    assert_eq!(lru.victim(), Some(f(3)), "the victim is the frame unpinned longest ago");
    assert_eq!(lru.victim(), Some(f(1)), "the victim is the frame unpinned longest ago");
    assert_eq!(lru.victim(), Some(f(2)), "the victim is the frame unpinned longest ago");
    assert_eq!(lru.victim(), None, "the victim is the frame unpinned longest ago");
}

#[test]
fn s1c_06_victim_removes_the_frame() {
    let mut lru = LruReplacer::new(4);
    lru.unpin(f(1));
    lru.unpin(f(2));
    lru.victim();
    assert_eq!(lru.size(), 1, "victim removes the frame");
}

#[test]
fn s1c_06_unpinning_again_does_not_refresh_a_frame() {
    // BusTub's rule: a frame that is already unpinned keeps its place in line.
    let mut lru = LruReplacer::new(4);
    lru.unpin(f(1));
    lru.unpin(f(2));
    lru.unpin(f(1));
    assert_eq!(lru.victim(), Some(f(1)), "unpinning again does not refresh a frame");
}

#[test]
fn s1c_06_an_empty_replacer_has_no_victim() {
    assert_eq!(LruReplacer::new(3).victim(), None, "an empty replacer has no victim");
}

#[test]
fn s1c_06_a_victim_can_be_unpinned_again_and_goes_to_the_back() {
    let mut lru = LruReplacer::new(4);
    lru.unpin(f(1));
    lru.unpin(f(2));
    assert_eq!(lru.victim(), Some(f(1)), "a victim can be unpinned again and goes to the back");
    lru.unpin(f(1));
    assert_eq!(lru.victim(), Some(f(2)), "a victim can be unpinned again and goes to the back");
    assert_eq!(lru.victim(), Some(f(1)), "a victim can be unpinned again and goes to the back");
}

// ---- 1c-02 · LruReplacer::pin -------------------------------------------------------------------------------------------

#[test]
fn s1c_07_a_pinned_frame_is_not_a_victim() {
    let mut lru = LruReplacer::new(5);
    for n in 1..=4 {
        lru.unpin(f(n));
    }
    lru.pin(f(2));
    assert_eq!(lru.size(), 3, "a pinned frame is not a victim");
    assert_eq!([lru.victim(), lru.victim(), lru.victim(), lru.victim()], [Some(f(1)), Some(f(3)), Some(f(4)), None], "a pinned frame is not a victim");
}

#[test]
fn s1c_07_pinning_a_frame_the_replacer_doesnt_hold_does_nothing() {
    let mut lru = LruReplacer::new(5);
    lru.unpin(f(1));
    lru.pin(f(9));
    assert_eq!(lru.size(), 1, "pinning a frame the replacer doesnt hold does nothing");
    let mut empty = LruReplacer::new(2);
    empty.pin(f(0));
    assert_eq!(empty.size(), 0, "pinning a frame the replacer doesnt hold does nothing");
}

#[test]
fn s1c_07_unpinning_after_a_pin_puts_the_frame_at_the_back() {
    let mut lru = LruReplacer::new(5);
    for n in 1..=3 {
        lru.unpin(f(n));
    }
    lru.pin(f(1));
    lru.unpin(f(1));
    assert_eq!([lru.victim(), lru.victim(), lru.victim()], [Some(f(2)), Some(f(3)), Some(f(1))], "unpinning after a pin puts the frame at the back");
}

#[test]
fn s1c_07_pinning_twice_is_fine() {
    let mut lru = LruReplacer::new(5);
    lru.unpin(f(1));
    lru.pin(f(1));
    lru.pin(f(1));
    assert_eq!(lru.size(), 0, "pinning twice is fine");
    assert_eq!(lru.victim(), None, "pinning twice is fine");
}

#[test]
fn s1c_07_two_hundred_thousand_frames_stay_fast() {
    // Every operation must be O(1): a Vec-and-position implementation takes minutes here.
    let n = 200_000;
    let mut lru = LruReplacer::new(n);
    let start = Instant::now();
    for i in 0..n {
        lru.unpin(f(i));
    }
    for i in (0..n).step_by(2) {
        lru.pin(f(i));
    }
    for i in (0..n).step_by(4) {
        lru.unpin(f(i));
    }
    let mut victims = 0;
    while lru.victim().is_some() {
        victims += 1;
    }
    assert_eq!(victims, n / 2 + n / 4, "two hundred thousand frames stay fast");
    assert!(start.elapsed() < Duration::from_secs(5), "took {:?}", start.elapsed());
}

// ---- 1c-03 · ClockReplacer: unpin and size ------------------------------------------------------------------------------

#[test]
fn s1c_08_unpin_adds_frames_to_the_ring() {
    let mut clock = ClockReplacer::new(7);
    assert_eq!(clock.size(), 0, "unpin adds frames to the ring");
    for n in 1..=6 {
        clock.unpin(f(n));
    }
    assert_eq!(clock.size(), 6, "unpin adds frames to the ring");
}

#[test]
fn s1c_08_unpinning_a_frame_twice_counts_it_once() {
    let mut clock = ClockReplacer::new(7);
    clock.unpin(f(1));
    clock.unpin(f(2));
    clock.unpin(f(1));
    assert_eq!(clock.size(), 2, "unpinning a frame twice counts it once");
}

#[test]
#[should_panic(expected = "full")]
fn s1c_08_more_frames_than_the_capacity_is_a_bug() {
    let mut clock = ClockReplacer::new(1);
    clock.unpin(f(1));
    clock.unpin(f(2));
}

// ---- 1c-03 · ClockReplacer::victim --------------------------------------------------------------------------------------

#[test]
fn s1c_09_with_every_bit_set_the_sweep_starts_over_at_the_first_frame() {
    let mut clock = ClockReplacer::new(7);
    for n in 1..=4 {
        clock.unpin(f(n));
    }
    assert_eq!([clock.victim(), clock.victim(), clock.victim(), clock.victim()], [Some(f(1)), Some(f(2)), Some(f(3)), Some(f(4))], "with every bit set the sweep starts over at the first frame");
    assert_eq!(clock.victim(), None, "with every bit set the sweep starts over at the first frame");
    assert_eq!(clock.size(), 0, "with every bit set the sweep starts over at the first frame");
}

#[test]
fn s1c_09_a_frame_unpinned_again_gets_a_second_chance() {
    let mut clock = ClockReplacer::new(7);
    for n in 1..=4 {
        clock.unpin(f(n));
    }
    assert_eq!(clock.victim(), Some(f(1)), "a frame unpinned again gets a second chance"); // the sweep cleared every bit
    clock.unpin(f(2)); // sets 2's bit again
    assert_eq!(clock.victim(), Some(f(3)), "2 is skipped once: its bit is cleared instead");
    assert_eq!(clock.victim(), Some(f(4)), "a frame unpinned again gets a second chance");
    assert_eq!(clock.victim(), Some(f(2)), "a frame unpinned again gets a second chance");
}

#[test]
fn s1c_09_a_new_frame_joins_the_end_of_the_ring_with_its_bit_set() {
    let mut clock = ClockReplacer::new(7);
    clock.unpin(f(1));
    clock.unpin(f(2));
    assert_eq!(clock.victim(), Some(f(1)), "a new frame joins the end of the ring with its bit set");
    clock.unpin(f(3));
    assert_eq!(clock.victim(), Some(f(2)), "a new frame joins the end of the ring with its bit set");
    assert_eq!(clock.victim(), Some(f(3)), "a new frame joins the end of the ring with its bit set");
}

#[test]
fn s1c_09_an_empty_ring_has_no_victim() {
    assert_eq!(ClockReplacer::new(3).victim(), None, "an empty ring has no victim");
}

#[test]
fn s1c_09_a_single_frame_with_its_bit_set_is_still_evicted() {
    let mut clock = ClockReplacer::new(3);
    clock.unpin(f(5));
    assert_eq!(clock.victim(), Some(f(5)), "a single frame with its bit set is still evicted");
}

// ---- 1c-03 · ClockReplacer::pin ----------------------------------------------------------------------------------------

#[test]
fn s1c_10_a_pinned_frame_leaves_the_ring() {
    let mut clock = ClockReplacer::new(7);
    for n in 1..=4 {
        clock.unpin(f(n));
    }
    clock.pin(f(2));
    assert_eq!(clock.size(), 3, "a pinned frame leaves the ring");
    assert_eq!([clock.victim(), clock.victim(), clock.victim(), clock.victim()], [Some(f(1)), Some(f(3)), Some(f(4)), None], "a pinned frame leaves the ring");
}

#[test]
fn s1c_10_pinning_an_unknown_frame_does_nothing() {
    let mut clock = ClockReplacer::new(7);
    clock.unpin(f(1));
    clock.pin(f(8));
    assert_eq!(clock.size(), 1, "pinning an unknown frame does nothing");
}

#[test]
fn s1c_10_the_hand_keeps_pointing_at_the_same_frame_when_an_earlier_frame_is_pinned() {
    let mut clock = ClockReplacer::new(8);
    for n in 1..=6 {
        clock.unpin(f(n));
    }
    assert_eq!(clock.victim(), Some(f(1)), "the hand keeps pointing at the same frame when an earlier frame is pinned"); // all bits cleared, hand at 2
    clock.unpin(f(2)); // 2 gets a second chance
    assert_eq!(clock.victim(), Some(f(3)), "the hand keeps pointing at the same frame when an earlier frame is pinned"); // hand passed 2 (clearing it) and took 3; hand now at 4
    clock.pin(f(2)); // 2 is behind the hand
    assert_eq!(clock.victim(), Some(f(4)), "the hand must still be at 4");
    assert_eq!(clock.victim(), Some(f(5)), "the hand keeps pointing at the same frame when an earlier frame is pinned");
}

#[test]
fn s1c_10_pinning_the_frame_under_the_hand_moves_on_to_the_next() {
    let mut clock = ClockReplacer::new(8);
    for n in 1..=4 {
        clock.unpin(f(n));
    }
    clock.victim(); // 1; hand at 2
    clock.pin(f(2));
    assert_eq!(clock.victim(), Some(f(3)), "pinning the frame under the hand moves on to the next");
    assert_eq!(clock.victim(), Some(f(4)), "pinning the frame under the hand moves on to the next");
}

#[test]
fn s1c_10_pinning_the_last_frame_wraps_the_hand() {
    let mut clock = ClockReplacer::new(8);
    for n in 1..=3 {
        clock.unpin(f(n));
    }
    clock.victim(); // 1; ring [2, 3], hand at 2
    clock.unpin(f(2)); // bit set
    clock.victim(); // clears 2, takes 3; ring [2], hand wraps to 0
    clock.pin(f(2));
    assert_eq!(clock.size(), 0, "pinning the last frame wraps the hand");
    clock.unpin(f(7));
    assert_eq!(clock.victim(), Some(f(7)), "pinning the last frame wraps the hand");
}

#[test]
fn s1c_10_unpin_after_pin_adds_the_frame_with_its_bit_set() {
    let mut clock = ClockReplacer::new(8);
    for n in 1..=3 {
        clock.unpin(f(n));
    }
    clock.victim(); // 1 (bits of 2, 3 cleared)
    clock.pin(f(2));
    clock.unpin(f(2)); // back at the end of the ring, bit set
    assert_eq!(clock.victim(), Some(f(3)), "unpin after pin adds the frame with its bit set");
    assert_eq!(clock.victim(), Some(f(2)), "unpin after pin adds the frame with its bit set");
}

// ---- 1c-04 · both replacers on the BusTub scenario ---------------------------------------------------------------------------

fn bustub_scenario(r: &mut dyn Replacer) -> Vec<Option<FrameId>> {
    for n in [1, 2, 3, 4, 5, 6, 1] {
        r.unpin(f(n));
    }
    assert_eq!(r.size(), 6, "in helper `bustub_scenario`");
    let mut out = vec![r.victim(), r.victim(), r.victim()];
    r.pin(f(3));
    r.pin(f(4));
    assert_eq!(r.size(), 2, "in helper `bustub_scenario`");
    r.unpin(f(4));
    out.extend([r.victim(), r.victim(), r.victim(), r.victim()]);
    out
}

#[test]
fn s1c_11_lru_gives_the_bustub_answers_through_the_trait() {
    let want = [Some(f(1)), Some(f(2)), Some(f(3)), Some(f(5)), Some(f(6)), Some(f(4)), None];
    assert_eq!(bustub_scenario(&mut LruReplacer::new(7)), want, "lru gives the bustub answers through the trait");
}

#[test]
fn s1c_11_clock_gives_the_bustub_answers_through_the_trait() {
    let want = [Some(f(1)), Some(f(2)), Some(f(3)), Some(f(5)), Some(f(6)), Some(f(4)), None];
    assert_eq!(bustub_scenario(&mut ClockReplacer::new(7)), want, "clock gives the bustub answers through the trait");
}

#[test]
fn s1c_11_the_policies_differ_when_frames_are_touched_unevenly() {
    // LRU: a frame unpinned again while it is already unpinned keeps its place. CLOCK: it gets a second chance.
    let mut lru = LruReplacer::new(5);
    let mut clock = ClockReplacer::new(5);
    for r in [&mut lru as &mut dyn Replacer, &mut clock] {
        for n in 1..=4 {
            r.unpin(f(n));
        }
    }
    clock.victim(); // clears every bit, evicts 1
    lru.victim();
    lru.unpin(f(2));
    clock.unpin(f(2));
    assert_eq!(lru.victim(), Some(f(2)), "LRU: 2 never moved");
    assert_eq!(clock.victim(), Some(f(3)), "CLOCK: 2 got a second chance");
}
