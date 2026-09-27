use solution::*;

fn p(x: i32, y: i32) -> Point {
    Point { x, y }
}

#[test]
fn prints() {
    check!(r#"Path [(1, 2), (3, 4)]"#, Path(vec![p(1, 2), p(3, 4)]).to_string(), "(1, 2) -> (3, 4)");
}

#[test]
fn empty() {
    check!(r#"Path []"#, Path(vec![]).to_string(), "(empty)");
}

#[test]
fn slice_like() {
    let path = Path::from(vec![p(0, 0), p(3, 4), p(3, 0)]);
    check!(r#"len, [1], length(&path) of [(0, 0), (3, 4), (3, 0)]"#, (path.len(), path[1], length(&path)), (3, p(3, 4), 11));
}

#[test]
fn collect_and_push() {
    let mut path: Path = (0..3).map(|i| p(i, i)).collect();
    path.push(p(9, 9));
    check!(r#"(0..3) mapped to (i, i) and collected, then push (9, 9)"#, path.to_string(), "(0, 0) -> (1, 1) -> (2, 2) -> (9, 9)");
}

#[test]
fn iter() {
    let path = Path::from(vec![p(1, 0), p(2, 0), p(3, 0)]);
    check!(r#"sum of x over the path"#, path.iter().map(|q| q.x).sum::<i32>(), 6);
}
