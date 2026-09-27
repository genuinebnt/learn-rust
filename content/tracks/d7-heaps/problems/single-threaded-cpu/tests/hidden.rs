use solution::*;

#[test]
fn single() {
    check!(r#"tasks = [(5, 5)]"#, get_order(&[(5, 5)]), vec![0]);
}

#[test]
fn clock_past_u32() {
    check!(r#"tasks = [(0, 4000000000), (1, 4000000000), (2, 1)]"#, get_order(&[(0, 4_000_000_000), (1, 4_000_000_000), (2, 1)]), vec![0, 2, 1]);
}

#[test]
fn long_idle_gap() {
    check!(r#"tasks = [(4000000000, 1), (5, 1)]"#, get_order(&[(4_000_000_000, 1), (5, 1)]), vec![1, 0]);
}

#[test]
fn max_times() {
    check!(r#"tasks = [(u32::MAX, u32::MAX), (u32::MAX, 0)]"#, get_order(&[(u32::MAX, u32::MAX), (u32::MAX, 0)]), vec![1, 0]);
}

#[test]
fn late_short_task_waits() {
    check!(r#"tasks = [(0, 10), (1, 1), (2, 5)]"#, get_order(&[(0, 10), (1, 1), (2, 5)]), vec![0, 1, 2]);
}

#[test]
fn zero_processing() {
    check!(r#"tasks = [(3, 0), (3, 0), (0, 3)]"#, get_order(&[(3, 0), (3, 0), (0, 3)]), vec![2, 0, 1]);
}

#[test]
fn shorter_wins_over_earlier() {
    check!(r#"tasks = [(0, 1), (1, 9), (1, 2)]"#, get_order(&[(0, 1), (1, 9), (1, 2)]), vec![0, 2, 1]);
}

#[test]
fn unsorted_arrivals() {
    check!(r#"tasks = [(9, 1), (3, 1), (6, 1), (0, 1)]"#, get_order(&[(9, 1), (3, 1), (6, 1), (0, 1)]), vec![3, 1, 2, 0]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(722);
    for _ in 0..300 {
        let n = rng.below(9);
        let tasks: Vec<(u32, u32)> = (0..n).map(|_| (rng.int(0, 10) as u32, rng.int(0, 4) as u32)).collect();
        let mut done = vec![false; n];
        let mut clock = 0u64;
        let mut want = Vec::new();
        while want.len() < n {
            let pick = (0..n).filter(|&i| !done[i] && tasks[i].0 as u64 <= clock).min_by_key(|&i| (tasks[i].1, i));
            match pick {
                Some(i) => {
                    done[i] = true;
                    clock += tasks[i].1 as u64;
                    want.push(i);
                }
                None => clock = (0..n).filter(|&i| !done[i]).map(|i| tasks[i].0 as u64).min().unwrap(),
            }
        }
        check!(format!("tasks = {tasks:?}"), get_order(&tasks), want);
    }
}

#[test]
fn scale_100k_all_at_once() {
    let mut rng = anneal_prelude::Rng::new(723);
    let tasks: Vec<(u32, u32)> = (0..100_000).map(|_| (0, rng.int(1, 1_000_000) as u32)).collect();
    let mut want: Vec<usize> = (0..tasks.len()).collect();
    want.sort_unstable_by_key(|&i| (tasks[i].1, i));
    check!("100000 tasks all enqueued at 0, random processing times", get_order(&tasks) == want, true);
}

#[test]
fn scale_100k_spread_out() {
    // Task i arrives at 10·i and takes 9 or 10: each one ends before the next arrives, often with an idle gap.
    let tasks: Vec<(u32, u32)> = (0..100_000u32).map(|i| (10 * i, 9 + i % 2)).collect();
    check!("100000 tasks arriving every 10, taking 9 or 10", get_order(&tasks) == (0..100_000).collect::<Vec<usize>>(), true);
}
