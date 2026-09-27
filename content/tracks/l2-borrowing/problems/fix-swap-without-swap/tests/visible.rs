use solution::*;

#[test]
fn swap_example() {
    check!(r#"["a", "b", "c"]; swap_items(0, 2)"#, { let mut v = ["a", "b", "c"].map(String::from); swap_items(&mut v, 0, 2); v }, ["c", "b", "a"].map(String::from));
}

#[test]
fn swap_same_slot() {
    check!(r#"["a", "b"]; swap_items(1, 1)"#, { let mut v = ["a", "b"].map(String::from); swap_items(&mut v, 1, 1); v }, ["a", "b"].map(String::from));
}

#[test]
fn rotate3_example() {
    check!(r#"["x", "y", "z"]; rotate3(0, 1, 2)"#, { let mut v = ["x", "y", "z"].map(String::from); rotate3(&mut v, 0, 1, 2); v }, ["y", "z", "x"].map(String::from));
}

#[test]
fn append_copy_example() {
    check!(r#"["ab", "cd"]; append_copy(0, 1)"#, { let mut v = ["ab", "cd"].map(String::from); append_copy(&mut v, 0, 1); v }, ["abcd", "cd"].map(String::from));
}

#[test]
fn append_copy_backwards() {
    check!(r#"["ab", "cd"]; append_copy(1, 0)"#, { let mut v = ["ab", "cd"].map(String::from); append_copy(&mut v, 1, 0); v }, ["ab", "cdab"].map(String::from));
}

#[test]
fn append_to_itself() {
    check!(r#"["ab"]; append_copy(0, 0)"#, { let mut v = ["ab"].map(String::from); append_copy(&mut v, 0, 0); v }, ["abab"].map(String::from));
}
