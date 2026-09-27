use solution::*;

#[test]
fn shout_none() {
    check!(r#"no nickname"#, { let mut u = User { name: "Ada".into(), nickname: None }; shout_nickname(&mut u); (u.nickname, u.name) }, (None, "Ada".to_string()));
}
