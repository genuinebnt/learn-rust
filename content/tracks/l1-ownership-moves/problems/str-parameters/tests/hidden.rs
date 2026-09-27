use solution::*;

#[test]
fn empty() {
    check!(r#""""#, initials(""), "");
}

#[test]
fn unicode() {
    check!(r#""élodie ünal""#, initials("élodie ünal"), "ÉÜ");
}

#[test]
fn only_spaces() {
    check!(r#""   ""#, initials("   "), "");
}

#[test]
fn extra_spaces() {
    check!(r#""  ada   lovelace  ""#, initials("  ada   lovelace  "), "AL");
}

#[test]
fn tabs_and_newlines() {
    check!(r#""ada\tbyron\nlovelace""#, initials("ada\tbyron\nlovelace"), "ABL");
}

#[test]
fn already_upper() {
    check!(r#""ALAN TURING""#, initials("ALAN TURING"), "AT");
}

#[test]
fn digits_and_marks() {
    check!(r#""3d printer -x""#, initials("3d printer -x"), "3P-");
}

#[test]
fn sharp_s() {
    check!(r#""ßen ob" (ß uppercases to SS)"#, initials("ßen ob"), "SSO");
}

#[test]
fn one_letter_words() {
    check!(r#""a b c""#, initials("a b c"), "ABC");
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1107);
    for _ in 0..300 {
        let len = rng.below(16);
        let name = rng.string(len, "abéß  \t");
        let mut want = String::new();
        let mut at_start = true;
        for c in name.chars() {
            if c.is_whitespace() {
                at_start = true;
            } else if at_start {
                want.extend(c.to_uppercase());
                at_start = false;
            }
        }
        check!(format!("full_name = {name:?}"), initials(&name), want);
    }
}

#[test]
fn many_words() {
    let name = "ab ".repeat(200_000);
    check!("\"ab ab … ab \" (200000 words)", initials(&name), "A".repeat(200_000));
}
