use solution::*;

#[test]
fn two_to_one() {
    check!(r#"s = "ab", t = "aa""#, is_isomorphic("ab", "aa"), false);
}

#[test]
fn badc_baba() {
    check!(r#"s = "badc", t = "baba""#, is_isomorphic("badc", "baba"), false);
}
