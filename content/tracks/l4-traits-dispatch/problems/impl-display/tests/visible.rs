use solution::*;

#[test]
fn thousands() {
    check!(r#"Money { cents: 123456 }"#, Money { cents: 123456 }.to_string(), "$1,234.56");
}

#[test]
fn negative_under_a_dollar() {
    check!(r#"Money { cents: -50 }"#, Money { cents: -50 }.to_string(), "-$0.50");
}

#[test]
fn width() {
    check!(r#"format!("[{:>10}]", Money { cents: 5 })"#, format!("[{:>10}]", Money { cents: 5 }), "[     $0.05]");
}

#[test]
fn password_hidden() {
    let c = Credentials { user: "bob".into(), password: "hunter2".into() };
    check!(r#"format!("{:?}", Credentials { user: "bob", password: "hunter2" })"#, format!("{:?}", c), r#"Credentials { user: "bob", password: "***" }"#);
}

#[test]
fn pretty_debug() {
    let c = Credentials { user: "bob".into(), password: "hunter2".into() };
    check!(r#"format!("{:#?}", Credentials { user: "bob", .. })"#, format!("{:#?}", c), "Credentials {\n    user: \"bob\",\n    password: \"***\",\n}");
}
