use solution::*;

#[test]
fn in_place() {
    let mut s = String::from("wow");
    exclaim(&mut s);
    exclaim(&mut s);
    check!(r#"exclaim twice on "wow""#, s, "wow!!".to_string());
}

#[test]
fn no_space() {
    check!(r#""single""#, first_word("single"), "single");
}

#[test]
fn leading_space() {
    check!(r#"" x""#, first_word(" x"), "");
}

#[test]
fn first_empty() {
    check!(r#""""#, first_word(""), "");
}

#[test]
fn two_spaces() {
    check!(r#""a  b""#, first_word("a  b"), "a");
}

#[test]
fn tab_is_not_a_space() {
    check!(r#""a\tb c""#, first_word("a\tb c"), "a\tb");
}

#[test]
fn trailing_space() {
    check!(r#""ab ""#, first_word("ab "), "ab");
}

#[test]
fn unicode() {
    check!(r#""héllo wörld" and greet("日本")"#, (first_word("héllo wörld"), greet("日本")), ("héllo", "Hello, 日本!".to_string()));
}

#[test]
fn exclaim_empty() {
    let mut s = String::new();
    exclaim(&mut s);
    check!(r#"exclaim on """#, s, "!".to_string());
}

#[test]
fn borrows_input() {
    let s = String::from("abc def");
    check!(r#"first_word points into its input"#, first_word(&s).as_ptr() == s.as_ptr(), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2201);
    for _ in 0..300 {
        let len = rng.below(10);
        let s = rng.string(len, "ab é\t");
        let want = match s.find(' ') {
            Some(i) => &s[..i],
            None => &s[..],
        };
        let mut shouted = s.clone();
        exclaim(&mut shouted);
        check!(format!("s = {s:?}"), (first_word(&s), greet(&s), shouted), (want, format!("Hello, {s}!"), format!("{s}!")));
    }
}
