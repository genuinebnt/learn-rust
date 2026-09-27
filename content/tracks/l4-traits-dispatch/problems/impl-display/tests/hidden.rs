use solution::*;

#[test]
fn zero() {
    check!(r#"Money { cents: 0 }"#, Money { cents: 0 }.to_string(), "$0.00");
}

#[test]
fn no_comma_below_1000() {
    check!(r#"Money { cents: 99999 }"#, Money { cents: 99999 }.to_string(), "$999.99");
}

#[test]
fn exactly_1000() {
    check!(r#"Money { cents: 100000 }"#, Money { cents: 100000 }.to_string(), "$1,000.00");
}

#[test]
fn i64_min() {
    check!(r#"Money { cents: i64::MIN }"#, Money { cents: i64::MIN }.to_string(), "-$92,233,720,368,547,758.08");
}

#[test]
fn i64_max() {
    check!(r#"Money { cents: i64::MAX }"#, Money { cents: i64::MAX }.to_string(), "$92,233,720,368,547,758.07");
}

#[test]
fn centered_fill() {
    check!(r#"format!("{:*^11}", Money { cents: -123 })"#, format!("{:*^11}", Money { cents: -123 }), "**-$1.23***");
}

#[test]
fn money_debug_still_derived() {
    check!(r#"format!("{:?}", Money { cents: 5 })"#, format!("{:?}", Money { cents: 5 }), "Money { cents: 5 }");
}

#[test]
fn user_is_escaped() {
    let c = Credentials { user: "bo\"b".into(), password: "x".into() };
    check!(r#"user with a quote: bo"b"#, format!("{:?}", c), r#"Credentials { user: "bo\"b", password: "***" }"#);
}

#[test]
fn empty_password_still_hidden() {
    let c = Credentials { user: String::new(), password: String::new() };
    check!(r#"password """#, format!("{:?}", c), r#"Credentials { user: "", password: "***" }"#);
}

#[test]
fn other_derives_kept() {
    let c = Credentials { user: "a".into(), password: "b".into() };
    check!(r#"c.clone() == c"#, c.clone() == c, true);
}

#[test]
fn nested_pretty() {
    let c = Credentials { user: "é".into(), password: "p".into() };
    check!(r#"format!("{:#?}", vec![Credentials])"#, format!("{:#?}", vec![c]), "[\n    Credentials {\n        user: \"é\",\n        password: \"***\",\n    },\n]");
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4403);
    for _ in 0..400 {
        let digits = rng.below(13) as u32;
        let cents = rng.int(-(10i64.pow(digits)), 10i64.pow(digits));
        let abs = cents.unsigned_abs();
        let mut parts = Vec::new();
        let mut d = abs / 100;
        loop {
            parts.push(d % 1000);
            d /= 1000;
            if d == 0 {
                break;
            }
        }
        let mut body = parts.pop().unwrap().to_string();
        while let Some(p) = parts.pop() {
            body.push_str(&format!(",{p:03}"));
        }
        let want = format!("{}${}.{:02}", if cents < 0 { "-" } else { "" }, body, abs % 100);
        check!(format!("cents = {cents}"), Money { cents }.to_string(), want);
    }
}
