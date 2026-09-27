use solution::*;

fn feed(sc: &mut StreamChecker, letters: &str) -> Vec<bool> {
    letters.chars().map(|c| sc.query(c)).collect()
}

#[test]
fn leetcode_stream() {
    let mut sc = StreamChecker::new(&["cd", "f", "kl"]);
    check!(r#"words = ["cd", "f", "kl"]; letters "abcdefghijkl""#, feed(&mut sc, "abcdefghijkl"), vec![false, false, false, true, false, true, false, false, false, false, false, true]);
}

#[test]
fn first_letter() {
    let mut sc = StreamChecker::new(&["a"]);
    check!(r#"words = ["a"]; letters "a""#, feed(&mut sc, "a"), vec![true]);
}

#[test]
fn suffix_not_prefix() {
    let mut sc = StreamChecker::new(&["ab"]);
    check!(r#"words = ["ab"]; letters "ba" (the stream must end with the word)"#, feed(&mut sc, "ba"), vec![false, false]);
}

#[test]
fn overlapping_matches() {
    let mut sc = StreamChecker::new(&["aaa"]);
    check!(r#"words = ["aaa"]; letters "aaaa""#, feed(&mut sc, "aaaa"), vec![false, false, true, true]);
}

#[test]
fn word_inside_a_longer_word() {
    let mut sc = StreamChecker::new(&["abc", "bc"]);
    check!(r#"words = ["abc", "bc"]; letters "abc""#, feed(&mut sc, "abc"), vec![false, false, true]);
}

#[test]
fn match_again_later() {
    let mut sc = StreamChecker::new(&["ab"]);
    check!(r#"words = ["ab"]; letters "abxab""#, feed(&mut sc, "abxab"), vec![false, true, false, false, true]);
}
