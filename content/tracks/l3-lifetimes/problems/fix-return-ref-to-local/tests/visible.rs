use solution::*;

#[test]
fn slug_example() {
    check!(r#"slug("Hello  Big World")"#, slug("Hello  Big World"), "hello-big-world");
}

#[test]
fn slug_borrows_when_unchanged() {
    check!(r#"slug("already-a-slug") is std::borrow::Cow::Borrowed"#, matches!(slug("already-a-slug"), std::borrow::Cow::Borrowed("already-a-slug")), true);
}

#[test]
fn clean_lines_example() {
    check!(r#"clean_lines("  a \n\n b\n   ")"#, clean_lines("  a \n\n b\n   "), vec!["a", "b"]);
}

#[test]
fn longest_file_name_example() {
    let paths = ["src/main.rs", "lib/very_long.rs", "x/y.rs"].map(String::from);
    check!(r#"["src/main.rs", "lib/very_long.rs", "x/y.rs"]"#, longest_file_name(&paths), Some("very_long.rs"));
}

#[test]
fn tie_goes_to_the_first() {
    let paths = ["a/xx", "b/yy"].map(String::from);
    check!(r#"["a/xx", "b/yy"]"#, longest_file_name(&paths), Some("xx"));
}

#[test]
fn empty_inputs() {
    check!(r#"slug(""), clean_lines(""), longest_file_name([])"#, (slug(""), clean_lines(""), longest_file_name(&[])), (std::borrow::Cow::Borrowed(""), Vec::<&str>::new(), None));
}
