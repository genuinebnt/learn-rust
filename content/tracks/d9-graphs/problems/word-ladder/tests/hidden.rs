use solution::*;

#[test]
fn one_step() {
    check!(r#"begin = "a", end = "c", words = ["a","b","c"]"#, ladder_length("a", "c", &["a", "b", "c"]), 2);
}

#[test]
fn disconnected() {
    check!(r#"begin = "ab", end = "xy", words = ["xy"]"#, ladder_length("ab", "xy", &["xy"]), 0);
}

#[test]
fn many_words() {
    let words: Vec<String> = (0..5000u32).map(|i| { let b = [b'a' + (i % 26) as u8, b'a' + (i / 26 % 26) as u8, b'a' + (i / 676 % 26) as u8]; String::from_utf8(b.to_vec()).unwrap() }).collect();
    let mut refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
    refs.push("zzz");
    check!(r#"5000 three-letter words"#, ladder_length("aaa", "zzz", &refs), 4);
}
