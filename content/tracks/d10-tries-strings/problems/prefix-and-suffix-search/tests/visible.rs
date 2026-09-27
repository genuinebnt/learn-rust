use solution::*;

#[test]
fn leetcode_apple() {
    let wf = WordFilter::new(&["apple"]);
    check!(r#"words = ["apple"], f("a", "e")"#, wf.f("a", "e"), Some(0));
}

#[test]
fn no_match() {
    let wf = WordFilter::new(&["apple"]);
    check!(r#"words = ["apple"], f("b", "e"), f("a", "x")"#, (wf.f("b", "e"), wf.f("a", "x")), (None, None));
}

#[test]
fn largest_index_wins() {
    let wf = WordFilter::new(&["apple", "ample", "angle"]);
    check!(r#"words = ["apple", "ample", "angle"], f("a", "le")"#, wf.f("a", "le"), Some(2));
}

#[test]
fn empty_prefix_and_suffix() {
    let wf = WordFilter::new(&["cat", "dog"]);
    check!(r#"words = ["cat", "dog"], f("", ""), f("", "t"), f("d", "")"#, (wf.f("", ""), wf.f("", "t"), wf.f("d", "")), (Some(1), Some(0), Some(1)));
}

#[test]
fn prefix_and_suffix_overlap() {
    let wf = WordFilter::new(&["abc"]);
    check!(r#"words = ["abc"], f("abc", "abc"), f("ab", "bc"), f("abc", "c")"#, (wf.f("abc", "abc"), wf.f("ab", "bc"), wf.f("abc", "c")), (Some(0), Some(0), Some(0)));
}

#[test]
fn both_must_hold_on_the_same_word() {
    let wf = WordFilter::new(&["ab", "cd"]);
    check!(r#"words = ["ab", "cd"], f("a", "d")"#, wf.f("a", "d"), None);
}
