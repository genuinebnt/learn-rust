use solution::*;

#[test]
fn empty_note() {
    check!(r#"note = "", magazine = """#, can_construct("", ""), true);
}

#[test]
fn missing_letter() {
    check!(r#"note = "z", magazine = "abc""#, can_construct("z", "abc"), false);
}

#[test]
fn empty_note_any_magazine() {
    check!(r#"note = "", magazine = "xyz""#, can_construct("", "xyz"), true);
}

#[test]
fn empty_magazine() {
    check!(r#"note = "a", magazine = """#, can_construct("a", ""), false);
}

#[test]
fn exact() {
    check!(r#"note = "abc", magazine = "cab""#, can_construct("abc", "cab"), true);
}

#[test]
fn note_longer() {
    check!(r#"note = "aab", magazine = "ab""#, can_construct("aab", "ab"), false);
}

#[test]
fn letter_z() {
    check!(r#"note = "zz", magazine = "zaz""#, can_construct("zz", "zaz"), true);
}

#[test]
fn one_short() {
    check!(r#"note = "aaaa", magazine = "aaab""#, can_construct("aaaa", "aaab"), false);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(8);
    for _ in 0..300 {
        let (n, m) = (rng.below(7), rng.below(9));
        let note = rng.string(n, "abc");
        let magazine = rng.string(m, "abc");
        let want = note.chars().all(|c| note.matches(c).count() <= magazine.matches(c).count());
        check!(format!("note = {note:?}, magazine = {magazine:?}"), can_construct(&note, &magazine), want);
    }
}

#[test]
fn scale_200k() {
    let magazine = "a".repeat(100_000) + &"b".repeat(100_000);
    let note = "b".repeat(100_000);
    check!("note = b × 100000, magazine = a × 100000 then b × 100000", can_construct(&note, &magazine), true);
}
