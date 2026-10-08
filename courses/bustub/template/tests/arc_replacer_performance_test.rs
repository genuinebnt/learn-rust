//! Port of `test/buffer/arc_replacer_performance_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database Group).
//! RecordAccess on a replacer with 256K frames, accessing pages in the middle of the list, must stay fast: average under 3 s per round.

use std::time::Instant;

use bustub::buffer::arc_replacer::ArcReplacer;
use bustub::common::config::{FrameId, PageId};

#[test]
fn record_access_performance_test() {
    let bpm_size: usize = 256 << 10; // 1GB of 4 KiB pages in BusTub's arithmetic
    let mut arc_replacer = ArcReplacer::new(bpm_size);
    // Fill up mfu with lots of pages
    for i in 0..bpm_size {
        arc_replacer.record_access(FrameId(i), PageId(i as i32));
        arc_replacer.set_evictable(FrameId(i), true);
    }
    // Keep accessing pages in the middle of the list
    let rounds = 10;
    let mut access_frame_id: usize = 256 << 9;
    let mut access_times = Vec::new();
    for _ in 0..rounds {
        let start = Instant::now();
        for _ in 0..bpm_size {
            arc_replacer.record_access(FrameId(access_frame_id), PageId(access_frame_id as i32));
            access_frame_id = (access_frame_id + 1) % bpm_size;
        }
        access_times.push(start.elapsed().as_millis() as f64);
    }
    let avg = access_times.iter().sum::<f64>() / 1000.0 / access_times.len() as f64;
    println!("Average time used: {avg}s. If this takes above 3s on average, RecordAccess is too slow on long lists.");
    assert!(avg < 3.0, "average {avg}s per round");
}
