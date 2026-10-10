//! Distance along a circular probe sequence.

pub fn probe_distance(home: usize, slot: usize, capacity: usize) -> usize {
    // @begin 0c-c3
    (slot + capacity - home) % capacity
    //~ if slot >= home { slot - home } else { home - slot }
    // @end
}
