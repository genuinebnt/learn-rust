use solution::*;

#[test]
fn example() {
    check!(r#"input "a:1\na:2\nb:3\na:4\n""#, key_runs("a:1\na:2\nb:3\na:4\n".as_bytes()).unwrap(), vec![("a".to_string(), 2), ("b".to_string(), 1), ("a".to_string(), 1)]);
}

#[test]
fn empty_input() {
    check!(r#"input """#, key_runs("".as_bytes()).unwrap(), Vec::<(String, usize)>::new());
}

#[test]
fn no_colon_uses_whole_line() {
    check!(r#"input "x\nx\ny\n""#, key_runs("x\nx\ny\n".as_bytes()).unwrap(), vec![("x".to_string(), 2), ("y".to_string(), 1)]);
}

#[test]
fn first_colon_only() {
    check!(r#"input "k:v:w\nk:z\n""#, key_runs("k:v:w\nk:z\n".as_bytes()).unwrap(), vec![("k".to_string(), 2)]);
}

#[test]
fn no_final_newline() {
    check!(r#"input "a:1\nb:2""#, key_runs("a:1\nb:2".as_bytes()).unwrap(), vec![("a".to_string(), 1), ("b".to_string(), 1)]);
}

#[test]
fn crlf() {
    check!(r#"input "a\r\na:2\r\n""#, key_runs("a\r\na:2\r\n".as_bytes()).unwrap(), vec![("a".to_string(), 2)]);
}
