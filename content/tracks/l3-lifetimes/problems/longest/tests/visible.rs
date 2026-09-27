use solution::*;

#[test]
fn longest_example() {
    check!(r#"longest("hi", "hello")"#, longest("hi", "hello"), "hello");
}

#[test]
fn longest_tie() {
    check!(r#"longest("ab", "cd")"#, longest("ab", "cd"), "ab");
}

#[test]
fn longest_of_outlives_the_slice() {
    let (a, b, c) = (String::from("a"), String::from("ccc"), String::from("bb"));
    let w = longest_of(&vec![a.as_str(), b.as_str(), c.as_str()]);
    check!(r#"longest_of a temporary Vec of ["a", "ccc", "bb"]"#, w, Some("ccc"));
}

#[test]
fn keep_longest_in_a_loop() {
    let text = String::from("ab\nabcd\nxyzw\na");
    let mut best: &str = "";
    let mut changed = 0;
    for line in text.lines() {
        if keep_longest(&mut best, line) {
            changed += 1;
        }
    }
    check!(r#"best = ""; keep_longest over lines of "ab\nabcd\nxyzw\na""#, (best, changed), ("abcd", 2));
}

#[test]
fn longest_of_empty() {
    check!(r#"longest_of([])"#, longest_of(&[]), None);
}
