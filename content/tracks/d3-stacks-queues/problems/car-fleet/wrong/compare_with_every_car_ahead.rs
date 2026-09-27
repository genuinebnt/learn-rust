pub fn car_fleet(target: u32, position: &[u32], speed: &[u32]) -> usize {
    let n = position.len();
    let time = |i: usize| (u64::from(target - position[i]), u64::from(speed[i]));
    (0..n)
        .filter(|&i| (0..n).all(|j| position[j] <= position[i] || { let ((d, s), (dj, sj)) = (time(i), time(j)); d * sj > dj * s }))
        .count()
}
