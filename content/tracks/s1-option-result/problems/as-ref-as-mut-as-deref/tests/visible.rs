use solution::*;

fn user(name: &str, nickname: Option<&str>, emails: Option<&[&str]>) -> User {
    User {
        name: name.to_string(),
        nickname: nickname.map(|n| n.to_string()),
        emails: emails.map(|es| es.iter().map(|e| e.to_string()).collect()),
    }
}

#[test]
fn nickname_wins() {
    let u = user("Ada", Some("ace"), None);
    let v = user("Ada", None, None);
    check!(r#"name "Ada", nickname "ace""#, (display_name(&u), display_name(&v)), ("ace", "Ada"));
}

#[test]
fn handles_in_order() {
    let u = user("Ada", Some("ace"), Some(&["a@x", "b@y"]));
    check!(r#"name "Ada", nickname "ace", emails ["a@x", "b@y"]"#, handles(&u), vec!["Ada", "ace", "a@x", "b@y"]);
}

#[test]
fn empty_email_list_has_no_primary() {
    let a = user("A", None, Some(&[]));
    let b = user("B", None, None);
    let c = user("C", None, Some(&["a@x"]));
    check!(r#"emails = Some([]), then None, then ["a@x"]"#, (primary_email(&a), primary_email(&b), primary_email(&c)), (None, None, Some("a@x")));
}

#[test]
fn add_email_creates_the_list() {
    let mut u = user("Ada", None, None);
    add_email(&mut u, "a@x".to_string());
    add_email(&mut u, "b@y".to_string());
    check!(r#"emails = None, add "a@x", add "b@y""#, u.emails, Some(vec!["a@x".to_string(), "b@y".to_string()]));
}

#[test]
fn shout_leaves_the_name_alone() {
    let mut u = user("Ada", Some("ace"), None);
    shout_nickname(&mut u);
    check!(r#"name "Ada", nickname "ace""#, (u.nickname, u.name), (Some("ACE".to_string()), "Ada".to_string()));
}
