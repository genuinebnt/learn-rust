//! Port of `test/buffer/clock_replacer_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database Group).

use bustub::buffer::clock_replacer::ClockReplacer;
use bustub::buffer::replacer::Replacer;
use bustub::common::config::FrameId;

#[test]
fn sample_test() {
    let mut clock_replacer = ClockReplacer::new(7);

    // Scenario: unpin six elements, i.e. add them to the replacer.
    for n in [1, 2, 3, 4, 5, 6, 1] {
        clock_replacer.unpin(FrameId(n));
    }
    assert_eq!(6, clock_replacer.size());

    // Scenario: get three victims from the clock.
    assert_eq!(Some(FrameId(1)), clock_replacer.victim());
    assert_eq!(Some(FrameId(2)), clock_replacer.victim());
    assert_eq!(Some(FrameId(3)), clock_replacer.victim());

    // Scenario: pin elements in the replacer.
    // Note that 3 has already been victimized, so pinning 3 should have no effect.
    clock_replacer.pin(FrameId(3));
    clock_replacer.pin(FrameId(4));
    assert_eq!(2, clock_replacer.size());

    // Scenario: unpin 4. We expect that the reference bit of 4 will be set to 1.
    clock_replacer.unpin(FrameId(4));

    // Scenario: continue looking for victims. We expect these victims.
    assert_eq!(Some(FrameId(5)), clock_replacer.victim());
    assert_eq!(Some(FrameId(6)), clock_replacer.victim());
    assert_eq!(Some(FrameId(4)), clock_replacer.victim());
}
