use solution::*;

#[test]
fn all_names_example() {
    check!(r#"all_names("ann\nbo")"#, all_names("ann\nbo"), vec!["ann", "bo", "root", "admin"]);
}

#[test]
fn all_names_borrows_input() {
    let text = String::from("zed");
    check!(r#"all_names of a String, first name points into it"#, all_names(&text)[0].as_ptr() == text.as_ptr(), true);
}

#[test]
fn keep_shortest_with_locals() {
    let local = String::from("ab");
    let slot = std::cell::Cell::new("longer");
    keep_shortest(&slot, &local);
    check!(r#"slot "longer"; keep_shortest(a local "ab")"#, slot.get(), "ab");
}

#[test]
fn shortest_line_example() {
    check!(r#"shortest_line("abc\nx\nyy")"#, shortest_line("abc\nx\nyy"), "x");
}

#[test]
fn apply_to_a_local() {
    let s = String::from("hello");
    check!(r#"apply(str::len, a local String)"#, apply(str::len, &s), 5);
}

#[test]
fn shorten_example() {
    check!(r#"shorten(["a"])"#, shorten(vec!["a"]), vec!["a"]);
}
