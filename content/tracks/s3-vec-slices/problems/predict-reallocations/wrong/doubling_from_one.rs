/// How many times the capacity changes while pushing 0..100 into Vec::<u32>::new().
pub const REALLOCATIONS: usize = 8;

/// The capacity after those 100 pushes.
pub const FINAL_CAPACITY: usize = 128;
