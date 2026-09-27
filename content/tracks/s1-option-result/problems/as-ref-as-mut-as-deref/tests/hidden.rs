use solution::*;

#[test]
fn shout_none() {
    check!(r#"no nickname"#, { let mut u = User { name: "Ada".into(), nickname: None }; shout_nickname(&mut u); (u.nickname, u.name) }, (None, "Ada".to_string()));
}

#[test]
fn empty_name_no_nickname() {
    let u = User { name: String::new(), nickname: None };
    check!(r#"name "", no nickname"#, display_name(&u), "");
}

#[test]
fn unicode_nickname() {
    let u = User { name: "Ada".into(), nickname: Some("zoë 🦀".into()) };
    check!(r#"name "Ada", nickname "zoë 🦀""#, display_name(&u), "zoë 🦀");
}

#[test]
fn shout_mixed() {
    check!(r#"nickname "a1-bC d""#, { let mut u = User { name: "x".into(), nickname: Some("a1-bC d".into()) }; shout_nickname(&mut u); u.nickname }, Some("A1-BC D".to_string()));
}

#[test]
fn shout_twice() {
    check!(r#"nickname "ace", shouted twice"#, { let mut u = User { name: "x".into(), nickname: Some("ace".into()) }; shout_nickname(&mut u); shout_nickname(&mut u); u.nickname }, Some("ACE".to_string()));
}

#[test]
fn shout_empty_nickname() {
    check!(r#"nickname """#, { let mut u = User { name: "Ada".into(), nickname: Some(String::new()) }; shout_nickname(&mut u); (u.nickname, u.name) }, (Some(String::new()), "Ada".to_string()));
}

#[test]
fn borrows_the_nickname() {
    let u = User { name: "Ada".into(), nickname: Some("ace".into()) };
    check!(r#"name "Ada", nickname "ace""#, std::ptr::eq(display_name(&u).as_ptr(), u.nickname.as_ref().map_or(std::ptr::null(), |n| n.as_ptr())), true);
}

#[test]
fn borrows_the_name() {
    let u = User { name: "Ada".into(), nickname: None };
    check!(r#"name "Ada", no nickname"#, std::ptr::eq(display_name(&u).as_ptr(), u.name.as_ptr()), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1304);
    for _ in 0..300 {
        let len = rng.below(4);
        let name = rng.string(len, "abZ ");
        let has = rng.bool();
        let len = rng.below(4);
        let nick = rng.string(len, "xyQ!");
        let nickname = if has { Some(nick.clone()) } else { None };
        let mut u = User { name: name.clone(), nickname: nickname.clone() };
        let desc = format!("name = {name:?}, nickname = {nickname:?}");
        let want = if has { nick.clone() } else { name.clone() };
        check!(desc.clone(), display_name(&u).to_string(), want);
        shout_nickname(&mut u);
        check!(format!("shout: {desc}"), (u.nickname, u.name), (nickname.map(|n| n.to_ascii_uppercase()), name));
    }
}
