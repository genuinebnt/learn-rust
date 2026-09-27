use solution::*;

#[test]
fn unclosed() {
    check!(r#""((""#, is_valid("(("), false);
}

#[test]
fn close_first() {
    check!(r#"")""#, is_valid(")"), false);
}

#[test]
fn deep() {
    let s = format!("{}{}", "(".repeat(100_000), ")".repeat(100_000));
    check!(r#"10⁵ nested pairs"#, is_valid(&s), true);
}

#[test]
fn single_open() {
    check!(r#""[""#, is_valid("["), false);
}

#[test]
fn reversed_pair() {
    check!(r#"")(""#, is_valid(")("), false);
}

#[test]
fn counts_match_order_wrong() {
    check!(r#""{(})""#, is_valid("{(})"), false);
}

#[test]
fn extra_closer_at_end() {
    check!(r#""(){}}""#, is_valid("(){}}"), false);
}

#[test]
fn long_valid() {
    check!(r#""{[()()]}[]""#, is_valid("{[()()]}[]"), true);
}

#[test]
fn odd_length() {
    check!(r#""(()""#, is_valid("(()"), false);
}

#[test]
fn random_vs_brute_force() {
    // Brute force: keep deleting adjacent matched pairs; valid iff nothing is left.
    fn brute(s: &str) -> bool {
        let mut s = s.to_string();
        loop {
            let t = s.replace("()", "").replace("[]", "").replace("{}", "");
            if t.len() == s.len() {
                return t.is_empty();
            }
            s = t;
        }
    }
    let mut rng = anneal_prelude::Rng::new(3001);
    let pairs = ["()", "[]", "{}"];
    for _ in 0..400 {
        let mut s = String::new();
        let k = rng.below(6);
        for _ in 0..k {
            // Inserting a matched pair anywhere keeps a valid string valid.
            let at = rng.below(s.len() / 2 + 1) * 2;
            let at = at.min(s.len());
            let p = *rng.pick(&pairs);
            s.insert_str(at, p);
        }
        if rng.bool() && !s.is_empty() {
            let i = rng.below(s.len());
            let c = *rng.pick(&['(', ')', '[', ']', '{', '}']);
            s.replace_range(i..i + 1, &c.to_string());
        }
        check!(format!("s = {s:?}"), is_valid(&s), brute(&s));
    }
}

#[test]
fn scale_200k_side_by_side() {
    let s = format!("{}{}", "([{".repeat(33_333), "}])".repeat(33_333)) + &"()".repeat(50_000);
    check!("33333 × \"([{\", 33333 × \"}])\", then 50000 × \"()\"", is_valid(&s), true);
}
