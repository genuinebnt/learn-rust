/// How many times the capacity changes while pushing 0..100 into Vec::<u32>::new().
/// 0 → 4 → 8 → 16 → 32 → 64 → 128.
pub const REALLOCATIONS: usize = 6;

/// The capacity after those 100 pushes.
pub const FINAL_CAPACITY: usize = 128;
