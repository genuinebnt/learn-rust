pub fn climb_stairs(n: u32) -> u64 {
    if n <= 1 { 1 } else { climb_stairs(n - 1) + climb_stairs(n - 2) }
}
