use solution::*;

#[test]
fn read_change_shrink_consume() {
    let mut words = vec!["hi".to_string(), "there".to_string(), "a".to_string()];
    let long = count_long(&words, 3);
    let best = longest(&words).map(str::len);
    shout_all(&mut words);
    drop_short(&mut words, 2);
    let sentence = into_sentence(words);
    check!("[\"hi\", \"there\", \"a\"]", (long, best, sentence), (1, Some(5), "HI THERE".to_string()));
}

#[test]
fn longest_borrows() {
    let w = vec!["ab".to_string(), "abc".to_string(), "xyz".to_string()];
    check!(r#"longest of ["ab", "abc", "xyz"] (last on a tie)"#, longest(&w), Some("xyz"));
}

#[test]
fn shout_in_place() {
    let mut w = vec!["ab".to_string(), "c".to_string()];
    check!(r#"["ab", "c"]"#, { shout_all(&mut w); w }, vec!["AB", "C"]);
}

#[test]
fn drop_short_keeps_order() {
    let mut w = vec!["ccc".to_string(), "a".to_string(), "bb".to_string(), "dddd".to_string()];
    check!(r#"["ccc", "a", "bb", "dddd"], min = 2"#, { drop_short(&mut w, 2); w }, vec!["ccc", "bb", "dddd"]);
}

#[test]
fn count_at_least() {
    let w = vec!["ab".to_string(), "abc".to_string(), "a".to_string()];
    check!(r#"["ab", "abc", "a"], min = 2 (at least, so "ab" counts)"#, count_long(&w, 2), 2);
}
