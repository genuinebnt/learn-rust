use solution::*;

#[test]
fn lone_star() {
    check!(r#"s = "*""#, check_valid_string("*"), true);
}

#[test]
fn lone_open() {
    check!(r#"s = "(""#, check_valid_string("("), false);
}

#[test]
fn lone_close() {
    check!(r#"s = ")""#, check_valid_string(")"), false);
}

#[test]
fn stars_only() {
    check!(r#"s = "**""#, check_valid_string("**"), true);
}

#[test]
fn three_stars_close() {
    check!(r#"s = "(((***""#, check_valid_string("(((***"), true);
}

#[test]
fn two_stars_short() {
    check!(r#"s = "(((**""#, check_valid_string("(((**"), false);
}

#[test]
fn open_left_at_end() {
    check!(r#"s = "(*)(""#, check_valid_string("(*)("), false);
}

#[test]
fn star_as_open_first() {
    check!(r#"s = "*)""#, check_valid_string("*)"), true);
}

#[test]
fn leetcode_long_false() {
    check!(r#"s = "((*)(*))((*""#, check_valid_string("((*)(*))((*"), false);
}

#[test]
fn leetcode_long_mixed() {
    check!(r#"s = "*()(())*()(()()((()(()()*)(*(())((((((((()*)(()(*)""#, check_valid_string("*()(())*()(()()((()(()()*)(*(())((((((((()*)(()(*)"), false);
}

#[test]
fn random_vs_brute_force() {
    // Try every reading of every star.
    fn ok(s: &[u8], open: usize) -> bool {
        let Some((&b, rest)) = s.split_first() else { return open == 0 };
        match b {
            b'(' => ok(rest, open + 1),
            b')' => open > 0 && ok(rest, open - 1),
            _ => ok(rest, open + 1) || ok(rest, open) || (open > 0 && ok(rest, open - 1)),
        }
    }
    let mut rng = anneal_prelude::Rng::new(821);
    for _ in 0..400 {
        let len = rng.below(9);
        let s = rng.string(len, "(*)");
        check!(format!("s = {s:?}"), check_valid_string(&s), ok(s.as_bytes(), 0));
    }
}

#[test]
fn scale_200k() {
    let fine = format!("{}{}", "(".repeat(100_000), "*".repeat(100_000));
    let extra_open = format!("({fine}");
    let extra_close = format!("{}{}", "*".repeat(100_000), ")".repeat(100_001));
    check!(
        "'(' × 100000 then '*' × 100000; with one more '(' in front; '*' × 100000 then ')' × 100001",
        (check_valid_string(&fine), check_valid_string(&extra_open), check_valid_string(&extra_close)),
        (true, false, false)
    );
}
