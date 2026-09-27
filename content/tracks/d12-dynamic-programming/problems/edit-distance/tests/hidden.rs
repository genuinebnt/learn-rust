use solution::*;

#[test]
fn both_empty() {
    check!(r#"a = "", b = """#, edit_distance("", ""), 0);
}

#[test]
fn one_replace() {
    check!(r#"a = "a", b = "b""#, edit_distance("a", "b"), 1);
}

#[test]
fn swap() {
    check!(r#"a = "ab", b = "ba""#, edit_distance("ab", "ba"), 2);
}

#[test]
fn kitten() {
    check!(r#"a = "kitten", b = "sitting""#, edit_distance("kitten", "sitting"), 3);
}

#[test]
fn insert_and_replace() {
    check!(r#"a = "abc", b = "yabd""#, edit_distance("abc", "yabd"), 2);
}

#[test]
fn plasma() {
    check!(r#"a = "plasma", b = "altruism""#, edit_distance("plasma", "altruism"), 6);
}

#[test]
fn cjk_insert() {
    check!(r#"a = "日本", b = "日本語""#, edit_distance("日本", "日本語"), 1);
}

#[test]
fn tilde() {
    check!(r#"a = "ñ", b = "n""#, edit_distance("ñ", "n"), 1);
}

#[test]
fn random_vs_brute_force() {
    fn dist(a: &[char], b: &[char]) -> usize {
        match (a, b) {
            ([], _) => b.len(),
            (_, []) => a.len(),
            ([x, ra @ ..], [y, rb @ ..]) if x == y => dist(ra, rb),
            ([_, ra @ ..], [_, rb @ ..]) => 1 + dist(ra, rb).min(dist(ra, b)).min(dist(a, rb)),
        }
    }
    let mut rng = anneal_prelude::Rng::new(1227);
    for _ in 0..300 {
        let (la, lb) = (rng.below(7), rng.below(7));
        let a = rng.string(la, "abé");
        let b = rng.string(lb, "abé");
        let (ca, cb): (Vec<char>, Vec<char>) = (a.chars().collect(), b.chars().collect());
        check!(format!("a = {a:?}, b = {b:?}"), edit_distance(&a, &b), dist(&ca, &cb));
    }
}

#[test]
fn scale_2000() {
    let a: String = (0..2000u64).map(|i| (b'a' + (i * 7919 % 26) as u8) as char).collect();
    let b: String = (0..2000u64).map(|i| (b'a' + ((i * 104_729 + 13) % 26) as u8) as char).collect();
    check!("a[i] = 'a' + (7919·i) % 26, b[i] = 'a' + (104729·i + 13) % 26, 2000 each", edit_distance(&a, &b), 1847);
}
