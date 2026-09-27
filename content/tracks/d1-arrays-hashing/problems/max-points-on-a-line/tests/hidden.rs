use solution::*;

#[test]
fn duplicates() {
    check!(r#"points = [(1,1), (1,1), (2,3)]"#, max_points(&[(1, 1), (1, 1), (2, 3)]), 3);
}

#[test]
fn vertical() {
    check!(r#"points = [(2,1), (2,5), (2,-3), (0,0)]"#, max_points(&[(2, 1), (2, 5), (2, -3), (0, 0)]), 3);
}

#[test]
fn empty() {
    check!(r#"points = []"#, max_points(&[]), 0);
}

#[test]
fn two() {
    check!(r#"points = [(0,0), (5,-3)]"#, max_points(&[(0, 0), (5, -3)]), 2);
}

#[test]
fn all_same() {
    check!(r#"points = [(4,4), (4,4), (4,4)]"#, max_points(&[(4, 4), (4, 4), (4, 4)]), 3);
}

#[test]
fn horizontal() {
    check!(r#"points = [(1,7), (-3,7), (9,7), (0,0)]"#, max_points(&[(1, 7), (-3, 7), (9, 7), (0, 0)]), 3);
}

#[test]
fn opposite_directions() {
    check!(r#"points = [(0,0), (1,-1), (-1,1), (2,2)]"#, max_points(&[(0, 0), (1, -1), (-1, 1), (2, 2)]), 3);
}

#[test]
fn float_trap() {
    check!(r#"points = [(0,0), (94911151,94911150), (94911152,94911151)]"#, max_points(&[(0, 0), (94_911_151, 94_911_150), (94_911_152, 94_911_151)]), 2);
}

#[test]
fn i32_extremes() {
    check!(r#"points = [(MIN,MIN), (0,0), (MAX,MAX)]"#, max_points(&[(i32::MIN, i32::MIN), (0, 0), (i32::MAX, i32::MAX)]), 3);
}

#[test]
fn random_vs_brute_force() {
    fn brute(p: &[(i32, i32)]) -> usize {
        let n = p.len();
        let mut best = n.min(2);
        for i in 0..n {
            for j in 0..n {
                if p[i] == p[j] {
                    continue;
                }
                let on = (0..n).filter(|&k| {
                    let (ax, ay) = ((p[j].0 - p[i].0) as i64, (p[j].1 - p[i].1) as i64);
                    let (bx, by) = ((p[k].0 - p[i].0) as i64, (p[k].1 - p[i].1) as i64);
                    ax * by == ay * bx
                }).count();
                best = best.max(on);
            }
        }
        // Every point identical: all of them are on any line through it.
        if n > 0 && p.iter().all(|&q| q == p[0]) {
            best = n;
        }
        best
    }
    let mut rng = anneal_prelude::Rng::new(29);
    for _ in 0..300 {
        let n = rng.below(8);
        let pts: Vec<(i32, i32)> = (0..n).map(|_| (rng.int(-3, 3) as i32, rng.int(-3, 3) as i32)).collect();
        check!(format!("points = {pts:?}"), max_points(&pts), brute(&pts));
    }
}

#[test]
fn scale_2000_points() {
    // 1500 points on y = 2x + 1, and 500 on a parabola far above it.
    let mut pts: Vec<(i32, i32)> = (0..1500).map(|x| (x, 2 * x + 1)).collect();
    pts.extend((0..500).map(|x| (x, x * x + 1_000_000)));
    check!("1500 points on y = 2x + 1, 500 on y = x² + 10⁶", max_points(&pts), 1500);
}
