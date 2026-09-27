use solution::*;

#[test]
fn single_open() {
    check!(r#"s = "(""#, min_add_to_make_valid("("), 1);
}

#[test]
fn single_close() {
    check!(r#"s = ")""#, min_add_to_make_valid(")"), 1);
}

#[test]
fn nested() {
    check!(r#"s = "((()))""#, min_add_to_make_valid("((()))"), 0);
}

#[test]
fn only_closes() {
    check!(r#"s = ")))""#, min_add_to_make_valid(")))"), 3);
}

#[test]
fn close_then_open() {
    check!(r#"s = "())(""#, min_add_to_make_valid("())("), 2);
}

#[test]
fn extra_in_the_middle() {
    check!(r#"s = "(()))(""#, min_add_to_make_valid("(()))("), 2);
}

#[test]
fn alternating() {
    check!(r#"s = "(()())""#, min_add_to_make_valid("(()())"), 0);
}

#[test]
fn wrapped_backwards() {
    check!(r#"s = ")()(""#, min_add_to_make_valid(")()("), 2);
}

#[test]
fn closes_then_opens() {
    check!(r#"s = ")))(((""#, min_add_to_make_valid(")))((("), 6);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(820);
    for _ in 0..400 {
        let len = rng.below(15);
        let s = rng.string(len, "()");
        // Strip matched pairs until none are left; what's left needs a partner each.
        let mut rest = s.clone();
        while rest.contains("()") {
            rest = rest.replace("()", "");
        }
        check!(format!("s = {s:?}"), min_add_to_make_valid(&s), rest.len());
    }
}

#[test]
fn scale_200k() {
    let nested = format!("{}{}", "(".repeat(100_000), ")".repeat(100_000));
    let backwards = format!("{}{}", ")".repeat(100_000), "(".repeat(100_000));
    check!("'(' × 100000 then ')' × 100000; then the reverse", (min_add_to_make_valid(&nested), min_add_to_make_valid(&backwards)), (0, 200_000));
}
