use solution::*;

#[test]
fn float_trap() {
    check!(r#"target 10⁹; arrival times 10⁻¹⁸ apart, equal in f64"#, car_fleet(1_000_000_000, &[0, 1], &[1_000_000_001, 1_000_000_000]), 2);
}

#[test]
fn never_catch_up() {
    check!(r#"target 10, position [0,5], speed [1,2]"#, car_fleet(10, &[0, 5], &[1, 2]), 2);
}

#[test]
fn would_catch_after_target() {
    check!(r#"target 10, position [0,9], speed [9,1]"#, car_fleet(10, &[0, 9], &[9, 1]), 2);
}

#[test]
fn blocked_by_middle() {
    check!(r#"target 20, position [0,10,15], speed [5,1,10]"#, car_fleet(20, &[0, 10, 15], &[5, 1, 10]), 2);
}

#[test]
fn slow_front_car() {
    check!(r#"target 10, position [0,1,2,3], speed [4,3,2,1]"#, car_fleet(10, &[0, 1, 2, 3], &[4, 3, 2, 1]), 1);
}

#[test]
fn u32_extremes() {
    check!(r#"target u32::MAX, position [0,1], speed [u32::MAX, u32::MAX - 1]"#, car_fleet(u32::MAX, &[0, 1], &[u32::MAX, u32::MAX - 1]), 1);
}

#[test]
fn same_speed() {
    check!(r#"target 10, position [1,2,3], speed [1,1,1]"#, car_fleet(10, &[1, 2, 3], &[1, 1, 1]), 3);
}

#[test]
fn unsorted_input() {
    check!(r#"target 10, position [6,0,3], speed [1,3,2]"#, car_fleet(10, &[6, 0, 3], &[1, 3, 2]), 1);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(3007);
    for _ in 0..300 {
        let target = 1 + rng.below(20) as u32;
        let mut all: Vec<u32> = (0..target).collect();
        rng.shuffle(&mut all);
        let n = rng.below(all.len().min(8) + 1);
        let position: Vec<u32> = all[..n].to_vec();
        let speed: Vec<u32> = rng.vec(n, 1, 5);
        // A car leads a fleet iff it arrives strictly later than every car ahead of it.
        let time = |i: usize| (u64::from(target - position[i]), u64::from(speed[i]));
        let want = (0..n)
            .filter(|&i| (0..n).all(|j| position[j] <= position[i] || { let ((d, s), (dj, sj)) = (time(i), time(j)); d * sj > dj * s }))
            .count();
        check!(format!("target {target}, position {position:?}, speed {speed:?}"), car_fleet(target, &position, &speed), want);
    }
}

#[test]
fn scale_200k_all_separate() {
    let position: Vec<u32> = (0..200_000).collect();
    let speed = vec![1u32; 200_000];
    check!("target 200000, positions 0..200000, all speed 1", car_fleet(200_000, &position, &speed), 200_000);
}
