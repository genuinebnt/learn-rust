use solution::*;

#[test]
fn all_names_empty() {
    check!(r#"all_names("")"#, all_names(""), vec!["root", "admin"]);
}

#[test]
fn shortest_none() {
    check!(r#"shortest_line("")"#, shortest_line(""), "(none)");
}

#[test]
fn shortest_tie_first() {
    check!(r#"shortest_line("ab\ncd")"#, shortest_line("ab\ncd"), "ab");
}

#[test]
fn shortest_empty_line() {
    check!(r#"shortest_line("a\n\nb")"#, shortest_line("a\n\nb"), "");
}

#[test]
fn keep_shortest_tie() {
    check!(r#"slot "ab"; keep_shortest("cd")"#, { let slot = std::cell::Cell::new("ab"); keep_shortest(&slot, "cd"); slot.get() }, "ab");
}

#[test]
fn apply_custom_fn() {
    fn commas(s: &str) -> usize {
        s.matches(',').count()
    }
    let s = String::from("a,b,c");
    check!(r#"apply(a fn counting commas, "a,b,c")"#, apply(commas, &s), 2);
}

#[test]
fn apply_to_a_literal() {
    check!(r#"apply(str::len, "")"#, apply(str::len, ""), 0);
}

#[test]
fn shortest_unicode_bytes() {
    check!(r#"shortest_line("éé\nabc")"#, shortest_line("éé\nabc"), "abc");
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6314);
    for _ in 0..300 {
        let len = rng.below(12);
        let text = rng.string(len, "ab\n");
        let mut best: Option<&str> = None;
        for l in text.lines() {
            if best.map_or(true, |b| l.len() < b.len()) {
                best = Some(l);
            }
        }
        check!(format!("shortest_line({text:?})"), shortest_line(&text), best.unwrap_or("(none)"));
        let mut want: Vec<&str> = text.lines().collect();
        want.push("root");
        want.push("admin");
        check!(format!("all_names({text:?})"), all_names(&text), want);
        check!(format!("apply(str::len, {text:?})"), apply(str::len, &text), text.len());
    }
}
