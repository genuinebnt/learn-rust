use solution::*;

#[test]
fn nested() {
    check!(r#"meetings = [(1, 10), (2, 3)]"#, can_attend_all(&[(1, 10), (2, 3)]), false);
}

#[test]
fn same_start() {
    check!(r#"meetings = [(1, 2), (1, 3)]"#, can_attend_all(&[(1, 2), (1, 3)]), false);
}

#[test]
fn identical() {
    check!(r#"meetings = [(1, 2), (1, 2)]"#, can_attend_all(&[(1, 2), (1, 2)]), false);
}

#[test]
fn negative_times() {
    check!(r#"meetings = [(-5, -1), (-1, 3)]"#, can_attend_all(&[(-5, -1), (-1, 3)]), true);
}

#[test]
fn i32_extremes_touch() {
    check!(r#"meetings = [(i32::MIN, 0), (0, i32::MAX)]"#, can_attend_all(&[(i32::MIN, 0), (0, i32::MAX)]), true);
}

#[test]
fn everything_covered() {
    check!(r#"meetings = [(i32::MIN, i32::MAX), (0, 1)]"#, can_attend_all(&[(i32::MIN, i32::MAX), (0, 1)]), false);
}

#[test]
fn clash_not_adjacent_in_input() {
    check!(r#"meetings = [(1, 5), (10, 12), (3, 4)]"#, can_attend_all(&[(1, 5), (10, 12), (3, 4)]), false);
}

#[test]
fn many_back_to_back() {
    check!(r#"meetings = [(4, 6), (0, 2), (2, 4), (6, 9)]"#, can_attend_all(&[(4, 6), (0, 2), (2, 4), (6, 9)]), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(804);
    for _ in 0..400 {
        let n = rng.below(7);
        let meetings: Vec<(i32, i32)> = (0..n)
            .map(|_| {
                let s = rng.int(-5, 20) as i32;
                let len = rng.int(1, 6) as i32;
                (s, s + len)
            })
            .collect();
        let want = (0..n).all(|i| (i + 1..n).all(|j| meetings[i].1 <= meetings[j].0 || meetings[j].1 <= meetings[i].0));
        check!(format!("meetings = {meetings:?}"), can_attend_all(&meetings), want);
    }
}

#[test]
fn scale_200k() {
    let fine: Vec<(i32, i32)> = (0..200_000).rev().map(|i| (2 * i, 2 * i + 2)).collect();
    let mut clash = fine.clone();
    clash[0].0 -= 1;
    check!("200000 back-to-back meetings in reverse order; then the last one starts 1 early", (can_attend_all(&fine), can_attend_all(&clash)), (true, false));
}
