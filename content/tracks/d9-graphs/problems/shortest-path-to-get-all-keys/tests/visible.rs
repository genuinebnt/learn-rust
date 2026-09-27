use solution::*;

#[test]
fn leetcode_example() {
    check!(r####"grid = ["@.a..", "###.#", "b.A.B"]"####, shortest_path_all_keys(&["@.a..", "###.#", "b.A.B"]), Some(8));
}

#[test]
fn pick_the_nearer_key_first() {
    check!(r#"grid = ["@..aA", "..B#.", "....b"]"#, shortest_path_all_keys(&["@..aA", "..B#.", "....b"]), Some(6));
}

#[test]
fn key_behind_its_own_lock() {
    check!(r#"grid = ["@Aa"]"#, shortest_path_all_keys(&["@Aa"]), None);
}

#[test]
fn walk_back_through_the_start() {
    check!(r#"grid = ["a.@.A.b"]"#, shortest_path_all_keys(&["a.@.A.b"]), Some(8));
}

#[test]
fn no_keys() {
    check!(r#"grid = ["@"]"#, shortest_path_all_keys(&["@"]), Some(0));
}
