use solution::*;

#[test]
fn keeps_order() {
    let mut v = vec![10, 11, 12, 13, 14];
    remove_indices(&mut v, &[3, 0, 3, 9]);
    check!(r#"v = [10, 11, 12, 13, 14], indices = [3, 0, 3, 9]"#, v, vec![11, 12, 14]);
}

#[test]
fn adjacent_indices() {
    let mut v = vec![1, 2, 3, 4];
    remove_indices(&mut v, &[1, 2]);
    check!(r#"v = [1, 2, 3, 4], indices = [1, 2]"#, v, vec![1, 4]);
}

#[test]
fn nothing_to_remove() {
    let mut v = vec![1, 2];
    remove_indices(&mut v, &[]);
    check!(r#"v = [1, 2], indices = []"#, v, vec![1, 2]);
}

#[test]
fn unordered_two() {
    let mut v: Vec<i32> = vec![10, 11, 12, 13, 14];
    let removed = remove_indices_unordered(&mut v, &[0, 3]);
    check!(r#"v = [10, 11, 12, 13, 14], indices = [0, 3]"#, (removed, v), (vec![13, 10], vec![14, 11, 12]));
}

#[test]
fn unordered_includes_last() {
    let mut v: Vec<i32> = vec![1, 2, 3];
    let removed = remove_indices_unordered(&mut v, &[2, 0]);
    check!(r#"v = [1, 2, 3], indices = [2, 0]"#, (removed, v), (vec![3, 1], vec![2]));
}
