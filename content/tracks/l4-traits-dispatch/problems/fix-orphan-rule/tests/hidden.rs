use solution::*;

fn p(x: i32, y: i32) -> Point {
    Point { x, y }
}

#[test]
fn single() {
    check!(r#"Path [(-1, 5)]"#, Path(vec![p(-1, 5)]).to_string(), "(-1, 5)");
}

#[test]
fn length_short_paths() {
    check!(r#"length of [] and [(1, 1)]"#, (length(&Path(vec![])), length(&Path(vec![p(1, 1)]))), (0, 0));
}

#[test]
fn length_extremes() {
    check!(r#"length of [(i32::MIN, 0), (i32::MAX, 0)]"#, length(&Path(vec![p(i32::MIN, 0), p(i32::MAX, 0)])), u32::MAX);
}

#[test]
fn format_in_sentence() {
    let path = Path(vec![p(0, 0), p(0, -1)]);
    check!(r#"format!("route: {}", path)"#, format!("route: {}", path), "route: (0, 0) -> (0, -1)");
}

#[test]
fn collect_empty() {
    check!(r#"an empty iterator collected"#, std::iter::empty::<Point>().collect::<Path>().to_string(), "(empty)");
}

#[test]
fn mutate_through_index() {
    let mut path = Path(vec![p(0, 0)]);
    path[0].x = 7;
    check!(r#"path[0].x = 7"#, path.to_string(), "(7, 0)");
}

#[test]
fn vec_still_usable() {
    let path = Path::from(vec![p(1, 1), p(2, 2)]);
    check!(r#"the inner Vec after building"#, path.0.len(), 2);
}

#[test]
fn sort_through_deref_mut() {
    let mut path = Path(vec![p(3, 0), p(1, 0)]);
    path.sort_by_key(|q| q.x);
    check!(r#"sort_by_key x on [(3, 0), (1, 0)]"#, path.to_string(), "(1, 0) -> (3, 0)");
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4417);
    for _ in 0..300 {
        let n = rng.below(5);
        let pts: Vec<Point> = (0..n).map(|_| p(rng.int(-9, 9) as i32, rng.int(-9, 9) as i32)).collect();
        let want = if n == 0 { "(empty)".to_string() } else { pts.iter().map(|q| format!("({}, {})", q.x, q.y)).collect::<Vec<_>>().join(" -> ") };
        let path: Path = pts.iter().copied().collect();
        check!(format!("{pts:?}"), path.to_string(), want);
        let len: u32 = pts.windows(2).map(|w| ((w[0].x - w[1].x).abs() + (w[0].y - w[1].y).abs()) as u32).sum();
        check!(format!("length {pts:?}"), length(&path), len);
    }
}
