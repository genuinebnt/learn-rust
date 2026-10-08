//! Port of `test/buffer/lru_replacer_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database Group).
//! `Victim(&value)` returning a bool becomes `victim()` returning an `Option`.

use bustub::buffer::lru_replacer::LruReplacer;
use bustub::buffer::replacer::Replacer;
use bustub::common::config::FrameId;

#[test]
fn sample_test() {
    let mut lru_replacer = LruReplacer::new(7);

    // Scenario: unpin six elements, i.e. add them to the replacer.
    for n in [1, 2, 3, 4, 5, 6, 1] {
        lru_replacer.unpin(FrameId(n));
    }
    assert_eq!(6, lru_replacer.size());

    // Scenario: get three victims from the lru.
    assert_eq!(Some(FrameId(1)), lru_replacer.victim());
    assert_eq!(Some(FrameId(2)), lru_replacer.victim());
    assert_eq!(Some(FrameId(3)), lru_replacer.victim());

    // Scenario: pin elements in the replacer.
    // Note that 3 has already been victimized, so pinning 3 should have no effect.
    lru_replacer.pin(FrameId(3));
    lru_replacer.pin(FrameId(4));
    assert_eq!(2, lru_replacer.size());

    // Scenario: unpin 4. 4 goes to the back of the line.
    lru_replacer.unpin(FrameId(4));

    // Scenario: continue looking for victims. We expect these victims.
    assert_eq!(Some(FrameId(5)), lru_replacer.victim());
    assert_eq!(Some(FrameId(6)), lru_replacer.victim());
    assert_eq!(Some(FrameId(4)), lru_replacer.victim());
}
