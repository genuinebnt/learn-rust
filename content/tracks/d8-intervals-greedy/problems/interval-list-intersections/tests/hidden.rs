use solution::*;

#[test]
fn identical() {
    check!(r#"a = [(1, 2), (4, 6)], b = [(1, 2), (4, 6)]"#, interval_intersection(&[(1, 2), (4, 6)], &[(1, 2), (4, 6)]), vec![(1, 2), (4, 6)]);
}

#[test]
fn negatives() {
    check!(r#"a = [(-5, -2), (0, 3)], b = [(-3, 1)]"#, interval_intersection(&[(-5, -2), (0, 3)], &[(-3, 1)]), vec![(-3, -2), (0, 1)]);
}

#[test]
fn i32_extremes() {
    check!(r#"a = [(MIN, MAX)], b = [(MIN, MIN), (MAX, MAX)]"#, interval_intersection(&[(i32::MIN, i32::MAX)], &[(i32::MIN, i32::MIN), (i32::MAX, i32::MAX)]), vec![(i32::MIN, i32::MIN), (i32::MAX, i32::MAX)]);
}

#[test]
fn points_meet() {
    check!(r#"a = [(3, 3)], b = [(3, 3)]"#, interval_intersection(&[(3, 3)], &[(3, 3)]), vec![(3, 3)]);
}

#[test]
fn interleaved() {
    check!(r#"a = [(1, 3), (5, 7), (9, 11)], b = [(2, 6), (8, 10)]"#, interval_intersection(&[(1, 3), (5, 7), (9, 11)], &[(2, 6), (8, 10)]), vec![(2, 3), (5, 6), (9, 10)]);
}

#[test]
fn swapped_arguments() {
    check!(r#"a = [(2, 6), (8, 10)], b = [(1, 3), (5, 7), (9, 11)]"#, interval_intersection(&[(2, 6), (8, 10)], &[(1, 3), (5, 7), (9, 11)]), vec![(2, 3), (5, 6), (9, 10)]);
}

#[test]
fn same_end() {
    check!(r#"a = [(1, 4), (6, 7)], b = [(2, 4), (5, 7)]"#, interval_intersection(&[(1, 4), (6, 7)], &[(2, 4), (5, 7)]), vec![(2, 4), (6, 7)]);
}

#[test]
fn first_list_empty() {
    check!(r#"a = [], b = [(1, 2)]"#, interval_intersection(&[], &[(1, 2)]), Vec::<(i32, i32)>::new());
}

#[test]
fn random_vs_brute_force() {
    fn list(rng: &mut anneal_prelude::Rng) -> Vec<(i32, i32)> {
        let n = rng.below(6);
        let mut out = Vec::new();
        let mut pos = rng.int(-3, 3) as i32;
        for _ in 0..n {
            let len = rng.int(0, 4) as i32;
            out.push((pos, pos + len));
            let gap = rng.int(1, 4) as i32;
            pos += len + gap;
        }
        out
    }
    let mut rng = anneal_prelude::Rng::new(812);
    for _ in 0..400 {
        let a = list(&mut rng);
        let b = list(&mut rng);
        let mut want = Vec::new();
        for &(s1, e1) in &a {
            for &(s2, e2) in &b {
                if s1.max(s2) <= e1.min(e2) {
                    want.push((s1.max(s2), e1.min(e2)));
                }
            }
        }
        want.sort_unstable();
        check!(format!("a = {a:?}, b = {b:?}"), interval_intersection(&a, &b), want);
    }
}

#[test]
fn scale_100k_each() {
    let a: Vec<(i32, i32)> = (0..100_000).map(|i| (4 * i, 4 * i + 2)).collect();
    let b: Vec<(i32, i32)> = (0..100_000).map(|i| (4 * i + 1, 4 * i + 3)).collect();
    let out = interval_intersection(&a, &b);
    check!("a = (4i, 4i + 2), b = (4i + 1, 4i + 3) for i in 0..100000", (out.len(), out[0], out[99_999]), (100_000, (1, 2), (399_997, 399_998)));
}
