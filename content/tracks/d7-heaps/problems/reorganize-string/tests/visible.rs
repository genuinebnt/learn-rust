use solution::*;

/// "ok" if `got` is a rearrangement of `s` with no two equal neighbours, otherwise what's wrong.
fn verdict(s: &str, got: Option<String>) -> String {
    let Some(t) = got else {
        return "None".to_string();
    };
    let (mut a, mut b): (Vec<char>, Vec<char>) = (s.chars().collect(), t.chars().collect());
    if let Some(i) = b.windows(2).position(|w| w[0] == w[1]) {
        return format!("{t:?} has {:?} twice in a row at char {i}", b[i]);
    }
    a.sort_unstable();
    b.sort_unstable();
    if a != b {
        return format!("{t:?} is not a rearrangement of the input");
    }
    "ok".to_string()
}

#[test]
fn leetcode_aab() {
    check!(r#"s = "aab""#, reorganize("aab"), Some("aba".to_string()));
}

#[test]
fn leetcode_impossible() {
    check!(r#"s = "aaab""#, reorganize("aaab"), None);
}

#[test]
fn empty() {
    check!(r#"s = """#, reorganize(""), Some(String::new()));
}

#[test]
fn single() {
    check!(r#"s = "a""#, reorganize("a"), Some("a".to_string()));
}

#[test]
fn any_valid_answer() {
    check!(r#"s = "aabb" (any valid answer)"#, verdict("aabb", reorganize("aabb")), "ok");
}

#[test]
fn just_possible() {
    check!(r#"s = "aaabb" (3 a in 5 chars still fits)"#, reorganize("aaabb"), Some("ababa".to_string()));
}

#[test]
fn unicode_chars() {
    check!(r#"s = "ééa""#, reorganize("ééa"), Some("éaé".to_string()));
}
