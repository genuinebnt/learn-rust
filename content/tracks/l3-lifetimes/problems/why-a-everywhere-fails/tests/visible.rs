use solution::*;

#[test]
fn split_lines_example() {
    check!(r#"split_lines("a,b\n,c", ',')"#, split_lines("a,b\n,c", ','), vec!["a", "b", "", "c"]);
}

#[test]
fn pieces_outlive_the_separator() {
    let text = String::from("x--y");
    let v: Vec<&str> = Splitter::new(&text, &String::from("--")).collect();
    check!(r#"collect pieces of "x--y" split on a temporary "--""#, v, vec!["x", "y"]);
}

#[test]
fn peek_does_not_advance() {
    let mut s = Splitter::new("a;b", ";");
    check!(r#""a;b" on ";": peek, next, peek"#, (s.peek(), s.next(), s.peek()), (Some("a"), Some("a"), Some("b")));
}

#[test]
fn like_str_split() {
    check!(r#"";a;;b;" on ";""#, Splitter::new(";a;;b;", ";").collect::<Vec<_>>(), vec!["", "a", "", "b", ""]);
}

#[test]
fn no_separator() {
    check!(r#""abc" on ",""#, Splitter::new("abc", ",").collect::<Vec<_>>(), vec!["abc"]);
}

#[test]
fn empty_text() {
    check!(r#""" on ",""#, Splitter::new("", ",").collect::<Vec<_>>(), vec![""]);
}
