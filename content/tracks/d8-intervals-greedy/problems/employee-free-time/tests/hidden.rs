use solution::*;

#[test]
fn nested() {
    check!(r#"schedule = [[(1, 10)], [(2, 3), (5, 6)]]"#, employee_free_time(&[vec![(1, 10)], vec![(2, 3), (5, 6)]]), Vec::<(i32, i32)>::new());
}

#[test]
fn long_then_short() {
    check!(r#"schedule = [[(1, 5), (20, 30)], [(2, 3), (6, 7)]]"#, employee_free_time(&[vec![(1, 5), (20, 30)], vec![(2, 3), (6, 7)]]), vec![(5, 6), (7, 20)]);
}

#[test]
fn negatives() {
    check!(r#"schedule = [[(-10, -5), (0, 2)], [(-7, -6), (3, 4)]]"#, employee_free_time(&[vec![(-10, -5), (0, 2)], vec![(-7, -6), (3, 4)]]), vec![(-5, 0), (2, 3)]);
}

#[test]
fn i32_extremes() {
    check!(r#"schedule = [[(-2147483648, -1)], [(1, 2147483647)]]"#, employee_free_time(&[vec![(i32::MIN, -1)], vec![(1, i32::MAX)]]), vec![(-1, 1)]);
}

#[test]
fn all_lists_empty() {
    check!(r#"schedule = [[], []]"#, employee_free_time(&[vec![], vec![]]), Vec::<(i32, i32)>::new());
}

#[test]
fn single_interval() {
    check!(r#"schedule = [[(0, 1)]]"#, employee_free_time(&[vec![(0, 1)]]), Vec::<(i32, i32)>::new());
}

#[test]
fn same_hours_for_all() {
    check!(r#"schedule = [[(1, 3), (5, 6)], [(1, 3), (5, 6)], [(1, 3), (5, 6)]]"#, employee_free_time(&[vec![(1, 3), (5, 6)], vec![(1, 3), (5, 6)], vec![(1, 3), (5, 6)]]), vec![(3, 5)]);
}

#[test]
fn relay_across_employees() {
    check!(r#"schedule = [[(1, 2), (3, 4), (5, 6)], [(2, 3)], [(6, 8), (10, 11)]]"#, employee_free_time(&[vec![(1, 2), (3, 4), (5, 6)], vec![(2, 3)], vec![(6, 8), (10, 11)]]), vec![(4, 5), (8, 10)]);
}

#[test]
fn touching_within_one_list() {
    check!(r#"schedule = [[(1, 2), (2, 3), (5, 6)]]"#, employee_free_time(&[vec![(1, 2), (2, 3), (5, 6)]]), vec![(3, 5)]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(827);
    for _ in 0..400 {
        let k = rng.below(4);
        let mut schedule: Vec<Vec<(i32, i32)>> = Vec::new();
        for _ in 0..k {
            let count = rng.below(4);
            let mut list = Vec::new();
            let mut t = rng.int(0, 4) as i32;
            for _ in 0..count {
                let len = rng.int(1, 4) as i32;
                list.push((t, t + len));
                let gap = rng.int(0, 4) as i32;
                t += len + gap;
            }
            schedule.push(list);
        }
        // Mark each busy unit [t, t + 1) on a small grid and read off the gaps.
        let mut busy = vec![false; 64];
        for &(s, e) in schedule.iter().flatten() {
            for t in s..e {
                busy[t as usize] = true;
            }
        }
        let mut want = Vec::new();
        if let (Some(first), Some(last)) = (busy.iter().position(|&b| b), busy.iter().rposition(|&b| b)) {
            let mut t = first;
            while t <= last {
                if busy[t] {
                    t += 1;
                } else {
                    let start = t;
                    while !busy[t] {
                        t += 1;
                    }
                    want.push((start as i32, t as i32));
                }
            }
        }
        check!(format!("schedule = {schedule:?}"), employee_free_time(&schedule), want);
    }
}

#[test]
fn scale_200k() {
    // Employee e works (e + 2000k, e + 2000k + 1): together busy 2000k..2000k + 1000, free after.
    let schedule: Vec<Vec<(i32, i32)>> = (0..1000).map(|e| (0..200).map(|k| (e + 2000 * k, e + 2000 * k + 1)).collect()).collect();
    let free = employee_free_time(&schedule);
    check!("1000 employees; employee e works (e + 2000k, e + 2000k + 1) for k in 0..200", (free.len(), free[0], free[198]), (199, (1000, 2000), (397_000, 398_000)));
}
