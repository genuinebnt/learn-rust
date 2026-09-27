use solution::*;

#[test]
fn empty_first() {
    check!(r#""", "X""#, full_name(String::new(), "X".into()), "X, ".to_string());
}

#[test]
fn zero() {
    check!(r#""a", 0"#, tag("a", 0), "a#0".to_string());
}

#[test]
fn max_id() {
    check!(r#""a", u32::MAX"#, tag("a", u32::MAX), "a#4294967295".to_string());
}

#[test]
fn ten() {
    check!(r#""v", 10"#, tag("v", 10), "v#10".to_string());
}

#[test]
fn empty_name_tag() {
    check!(r#""", 5"#, tag("", 5), "#5".to_string());
}

#[test]
fn both_empty() {
    check!(r#""", """#, full_name(String::new(), String::new()), ", ".to_string());
}

#[test]
fn unicode_names() {
    check!(r#""Zoë", "Ünal""#, full_name("Zoë".into(), "Ünal".into()), "Ünal, Zoë".to_string());
}

#[test]
fn unicode_tag() {
    check!(r#""日本", 3"#, tag("日本", 3), "日本#3".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2203);
    for _ in 0..300 {
        let (l1, l2) = (rng.below(6), rng.below(6));
        let first = rng.string(l1, "ab é");
        let last = rng.string(l2, "xy ü");
        let id = rng.next_u64() as u32 >> rng.below(32);
        let want = (format!("{last}, {first}"), format!("{first}#{id}"));
        check!(format!("first = {first:?}, last = {last:?}, id = {id}"), (full_name(first.clone(), last.clone()), tag(&first, id)), want);
    }
}
