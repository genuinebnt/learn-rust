use solution::*;

#[test]
fn rotate_two() {
    check!(r#"v = [1, 2, 3, 4, 5], k = 2"#, { let mut v = [1, 2, 3, 4, 5]; rotate_right(&mut v, 2); v }, [4, 5, 1, 2, 3]);
}

#[test]
fn rotate_leetcode_189() {
    check!(r#"v = [1, 2, 3, 4, 5, 6, 7], k = 3"#, { let mut v = [1, 2, 3, 4, 5, 6, 7]; rotate_right(&mut v, 3); v }, [5, 6, 7, 1, 2, 3, 4]);
}

#[test]
fn move_right() {
    let mut v = ["a", "b", "c", "d", "e"];
    move_item(&mut v, 1, 3);
    check!(r#"v = ["a", "b", "c", "d", "e"], from = 1, to = 3"#, v, ["a", "c", "d", "b", "e"]);
}

#[test]
fn move_left() {
    let mut v = ["a", "b", "c", "d", "e"];
    move_item(&mut v, 4, 0);
    check!(r#"v = ["a", "b", "c", "d", "e"], from = 4, to = 0"#, v, ["e", "a", "b", "c", "d"]);
}

#[test]
fn swap_odd_length() {
    check!(r#"v = [1, 2, 3, 4, 5]"#, { let mut v = [1, 2, 3, 4, 5]; swap_pairs(&mut v); v }, [2, 1, 4, 3, 5]);
}
