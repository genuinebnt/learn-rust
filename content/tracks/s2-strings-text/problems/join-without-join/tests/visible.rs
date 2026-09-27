use solution::*;

#[test]
fn join_three() {
    check!(r#"words = ["a", "bc", "d"], sep = ", ""#, join_words(&["a", "bc", "d"], ", "), "a, bc, d".to_string());
}

#[test]
fn join_one_allocation() {
    let (s, n) = anneal_prelude::allocs(|| join_words(&["abc"; 10], ", "));
    check!(r#"words = ["abc"; 10], sep = ", ""#, (s.len(), s.capacity(), n.count), (48, 48, 1));
}

#[test]
fn squeeze_runs() {
    let mut s = String::from("  a \t b  c ");
    squeeze(&mut s);
    check!(r#""  a \t b  c ""#, s, "a b c".to_string());
}

#[test]
fn pop_crlf_line() {
    let mut buf = String::from("GET /\r\nHost: x\r\npart");
    let first = pop_line(&mut buf);
    check!(r#""GET /\r\nHost: x\r\npart""#, (first, buf.as_str()), (Some("GET /".to_string()), "Host: x\r\npart"));
}

#[test]
fn pop_incomplete_line() {
    let mut buf = String::from("partial");
    check!(r#""partial""#, (pop_line(&mut buf), buf.as_str()), (None, "partial"));
}
