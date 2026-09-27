use solution::*;

#[test]
fn nested() {
    check!(r#"intervals = [(1, 10), (2, 3)]"#, erase_overlap_intervals(&[(1, 10), (2, 3)]), 1);
}

#[test]
fn staircase() {
    check!(r#"intervals = [(0, 2), (1, 3), (2, 4), (3, 5)]"#, erase_overlap_intervals(&[(0, 2), (1, 3), (2, 4), (3, 5)]), 2);
}

#[test]
fn negatives() {
    check!(r#"intervals = [(-3, -1), (-2, 0), (-1, 1)]"#, erase_overlap_intervals(&[(-3, -1), (-2, 0), (-1, 1)]), 1);
}

#[test]
fn i32_extremes() {
    check!(r#"intervals = [(MIN, MAX), (MIN, 0), (0, MAX)]"#, erase_overlap_intervals(&[(i32::MIN, i32::MAX), (i32::MIN, 0), (0, i32::MAX)]), 1);
}

#[test]
fn earliest_start_is_a_trap() {
    check!(r#"intervals = [(1, 10), (2, 3), (4, 5)]"#, erase_overlap_intervals(&[(1, 10), (2, 3), (4, 5)]), 1);
}

#[test]
fn same_end() {
    check!(r#"intervals = [(1, 3), (2, 3), (0, 3)]"#, erase_overlap_intervals(&[(1, 3), (2, 3), (0, 3)]), 2);
}

#[test]
fn disjoint_unsorted() {
    check!(r#"intervals = [(5, 6), (1, 2), (3, 4)]"#, erase_overlap_intervals(&[(5, 6), (1, 2), (3, 4)]), 0);
}

#[test]
fn leetcode_mixed() {
    check!(r#"intervals = [(-52, 31), (-73, -26), (82, 97), (-65, -11), (-62, -49), (95, 99), (58, 95), (-31, 49), (66, 98), (-63, 2), (30, 47), (-40, -26)]"#, erase_overlap_intervals(&[(-52, 31), (-73, -26), (82, 97), (-65, -11), (-62, -49), (95, 99), (58, 95), (-31, 49), (66, 98), (-63, 2), (30, 47), (-40, -26)]), 7);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(809);
    for _ in 0..300 {
        let n = rng.below(9);
        let intervals: Vec<(i32, i32)> = (0..n)
            .map(|_| {
                let s = rng.int(-5, 15) as i32;
                let len = rng.int(1, 6) as i32;
                (s, s + len)
            })
            .collect();
        let mut most = 0;
        for mask in 0u32..1 << n {
            let kept: Vec<(i32, i32)> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| intervals[i]).collect();
            let ok = (0..kept.len()).all(|i| (i + 1..kept.len()).all(|j| kept[i].1 <= kept[j].0 || kept[j].1 <= kept[i].0));
            if ok {
                most = most.max(kept.len());
            }
        }
        check!(format!("intervals = {intervals:?}"), erase_overlap_intervals(&intervals), n - most);
    }
}

#[test]
fn scale_200k() {
    // Pairs (2i, 2i + 2) and (2i + 1, 2i + 3): the (2i, 2i + 2) ones can all be kept.
    let intervals: Vec<(i32, i32)> = (0..100_000).rev().flat_map(|i| [(2 * i + 1, 2 * i + 3), (2 * i, 2 * i + 2)]).collect();
    check!("(2i, 2i + 2) and (2i + 1, 2i + 3) for i in 0..100000", erase_overlap_intervals(&intervals), 100_000);
}
