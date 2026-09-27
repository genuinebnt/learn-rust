use solution::*;

#[test]
fn longer_second() {
    check!(r#""abc", "abcd""#, longest("abc", "abcd"), "abcd");
}

#[test]
fn owned_inputs() {
    let a = String::from("xy");
    let b = String::from("xyz!");
    check!(r#"two Strings"#, longest(&a, &b), "xyz!");
}

#[test]
fn tie_returns_first_pointer() {
    let a = String::from("ab");
    let b = String::from("ab");
    check!(r#""ab", "ab" (two different Strings)"#, std::ptr::eq(longest(&a, &b), a.as_str()), true);
}

#[test]
fn second_empty() {
    check!(r#""a", """#, longest("a", ""), "a");
}

#[test]
fn unicode() {
    check!(r#""é", "ab c""#, longest("é", "ab c"), "ab c");
}

#[test]
fn spaces_count() {
    check!(r#""a  ", "bc""#, longest("a  ", "bc"), "a  ");
}

#[test]
fn used_while_both_live() {
    let a = String::from("hello");
    let len;
    {
        let b = String::from("hi");
        len = longest(&a, &b).len();
    }
    check!(r#"result used inside the scope of the shorter-lived String"#, len, 5);
}

#[test]
fn long_strings() {
    check!(r#"10000 × "a" vs 10001 × "b""#, longest(&"a".repeat(10_000), &"b".repeat(10_001)).len(), 10_001);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(303);
    for _ in 0..300 {
        let (la, lb) = (rng.below(5), rng.below(5));
        let a = rng.string(la, "xy");
        let b = rng.string(lb, "xy");
        let want = if b.len() > a.len() { b.as_str() } else { a.as_str() };
        check!(format!("a = {a:?}, b = {b:?}"), std::ptr::eq(longest(&a, &b), want), true);
    }
}
