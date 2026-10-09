//! Distance along a circular probe sequence.

pub fn probe_distance(home: usize, slot: usize, capacity: usize) -> usize {
    if slot >= home { slot - home } else { home - slot }
}
