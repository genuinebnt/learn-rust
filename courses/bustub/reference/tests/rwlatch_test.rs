//! Port of `test/common/rwlatch_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database Group).

use bustub::common::rwlatch::ReaderWriterLatch;
use std::sync::Arc;
use std::thread;

/// The C++ test keeps `count_` next to a `ReaderWriterLatch mutex_`; here the latch owns the count.
struct Counter {
    count: ReaderWriterLatch<i32>,
}

impl Counter {
    fn new() -> Counter {
        Counter { count: ReaderWriterLatch::new(0) }
    }

    fn add(&self, num: i32) {
        *self.count.write() += num;
    }

    fn read(&self) -> i32 {
        *self.count.read()
    }
}

#[test]
fn basic_test() {
    let num_threads = 100;
    let counter = Arc::new(Counter::new());
    counter.add(5);
    let mut threads = Vec::new();
    for tid in 0..num_threads {
        let counter = Arc::clone(&counter);
        if tid % 2 == 0 {
            threads.push(thread::spawn(move || {
                counter.read();
            }));
        } else {
            threads.push(thread::spawn(move || counter.add(1)));
        }
    }
    for t in threads {
        t.join().unwrap();
    }
    assert_eq!(counter.read(), 55);
}
