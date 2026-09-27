use solution::*;

#[test]
fn too_long_alone() {
    check!(r#"courses = [(6, 5)]"#, schedule_course(&[(6, 5)]), 0);
}

#[test]
fn same_deadline() {
    check!(r#"courses = [(2, 2), (2, 2)]"#, schedule_course(&[(2, 2), (2, 2)]), 1);
}

#[test]
fn back_to_back() {
    check!(r#"courses = [(1, 2), (2, 3)]"#, schedule_course(&[(1, 2), (2, 3)]), 2);
}

#[test]
fn shorter_pair_wins() {
    check!(r#"courses = [(5, 5), (4, 6), (2, 6)]"#, schedule_course(&[(5, 5), (4, 6), (2, 6)]), 2);
}

#[test]
fn leetcode_eight() {
    check!(r#"courses = [(5, 15), (3, 19), (6, 7), (2, 10), (5, 16), (8, 14), (10, 11), (2, 19)]"#, schedule_course(&[(5, 15), (3, 19), (6, 7), (2, 10), (5, 16), (8, 14), (10, 11), (2, 19)]), 5);
}

#[test]
fn leetcode_seven() {
    check!(r#"courses = [(7, 17), (3, 12), (10, 20), (9, 10), (5, 20), (10, 19), (4, 18)]"#, schedule_course(&[(7, 17), (3, 12), (10, 20), (9, 10), (5, 20), (10, 19), (4, 18)]), 4);
}

#[test]
fn time_past_u32() {
    check!(r#"courses = [(4294967295, 4294967295), (4294967295, 4294967295)]"#, schedule_course(&[(u32::MAX, u32::MAX), (u32::MAX, u32::MAX)]), 1);
}

#[test]
fn unsorted_input() {
    check!(r#"courses = [(2, 10), (9, 9)]"#, schedule_course(&[(2, 10), (9, 9)]), 1);
}

#[test]
fn duration_order_trap() {
    check!(r#"courses = [(1, 100), (99, 99), (1, 2)]"#, schedule_course(&[(1, 100), (99, 99), (1, 2)]), 2);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(829);
    for _ in 0..300 {
        let n = rng.below(9);
        let courses: Vec<(u32, u32)> = (0..n).map(|_| (rng.int(1, 6) as u32, rng.int(1, 15) as u32)).collect();
        // A set fits exactly when it fits in deadline order.
        let mut want = 0;
        for mask in 0u32..1 << n {
            let mut chosen: Vec<(u32, u32)> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| courses[i]).collect();
            chosen.sort_unstable_by_key(|c| c.1);
            let mut t = 0;
            if chosen.iter().all(|&(d, last)| {
                t += d;
                t <= last
            }) {
                want = want.max(chosen.len());
            }
        }
        check!(format!("courses = {courses:?}"), schedule_course(&courses), want);
    }
}

#[test]
fn scale_200k() {
    let same = vec![(1u32, 100_000u32); 200_000];
    let spread: Vec<(u32, u32)> = (0..200_000u32).rev().map(|i| (2, 2 * i + 2)).collect();
    check!("(1, 100000) × 200000; (2, 2i + 2) for i in 0..200000", (schedule_course(&same), schedule_course(&spread)), (100_000, 200_000));
}
