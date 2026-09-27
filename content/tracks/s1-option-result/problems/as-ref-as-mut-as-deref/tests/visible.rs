use solution::*;

#[test]
fn nickname_wins() {
    let u = User { name: "Ada".into(), nickname: Some("ace".into()) };
    check!(r#"name "Ada", nickname "ace""#, display_name(&u), "ace");
}

#[test]
fn falls_back() {
    let u = User { name: "Ada".into(), nickname: None };
    check!(r#"name "Ada", no nickname"#, display_name(&u), "Ada");
}

#[test]
fn shout() {
    check!(r#"nickname "ace""#, { let mut u = User { name: "Ada".into(), nickname: Some("ace".into()) }; shout_nickname(&mut u); u.nickname }, Some("ACE".to_string()));
}

#[test]
fn empty_nickname_still_wins() {
    let u = User { name: "Ada".into(), nickname: Some(String::new()) };
    check!(r#"name "Ada", nickname """#, display_name(&u), "");
}

#[test]
fn shout_leaves_the_name_alone() {
    check!(r#"name "Ada", nickname "ace""#, { let mut u = User { name: "Ada".into(), nickname: Some("ace".into()) }; shout_nickname(&mut u); (u.nickname, u.name) }, (Some("ACE".to_string()), "Ada".to_string()));
}
