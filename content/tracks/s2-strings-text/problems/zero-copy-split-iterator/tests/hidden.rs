use solution::*;

#[test]
fn trailing() {
    check!(r#""a,", ','"#, split_on("a,", ',').collect::<Vec<_>>(), vec!["a", ""]);
}

#[test]
fn reversed() {
    check!(r#""a,b,c", ',' reversed"#, split_on("a,b,c", ',').rev().collect::<Vec<_>>(), vec!["c", "b", "a"]);
}

#[test]
fn both_ends() {
    let mut it = split_on("1-2-3-4", '-');
    check!(r#""1-2-3-4": next, next_back, next, next_back, next"#, (it.next(), it.next_back(), it.next(), it.next_back(), it.next()), (Some("1"), Some("4"), Some("2"), Some("3"), None));
}

#[test]
fn unicode_delim() {
    check!(r#""x→y→", '→'"#, split_on("x→y→", '→').collect::<Vec<_>>(), vec!["x", "y", ""]);
}

#[test]
fn items_outlive_iterator() {
    let text = String::from("ab cd");
    let first;
    {
        let mut it = split_on(&text, ' ');
        first = it.next();
    }
    check!(r#"keep the first piece after dropping the iterator"#, first, Some("ab"));
}

#[test]
fn matches_std() {
    let s = ";;a;bc;;d;";
    let ours: Vec<&str> = split_on(s, ';').collect();
    let theirs: Vec<&str> = s.split(';').collect();
    check!(r#"same as str::split on a mixed string"#, ours == theirs, true);
}
