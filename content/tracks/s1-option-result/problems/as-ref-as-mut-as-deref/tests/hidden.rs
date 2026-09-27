use solution::*;

fn user(name: &str, nickname: Option<&str>, emails: Option<&[&str]>) -> User {
    User {
        name: name.to_string(),
        nickname: nickname.map(|n| n.to_string()),
        emails: emails.map(|es| es.iter().map(|e| e.to_string()).collect()),
    }
}

#[test]
fn empty_nickname_still_wins() {
    let u = user("Ada", Some(""), None);
    check!(r#"name "Ada", nickname """#, display_name(&u), "");
}

#[test]
fn handles_without_extras() {
    let a = user("Ada", None, None);
    let b = user("Ada", None, Some(&[]));
    check!(r#"name "Ada" only; then emails = Some([])"#, (handles(&a), handles(&b)), (vec!["Ada"], vec!["Ada"]));
}

#[test]
fn handles_keep_an_empty_nickname() {
    let u = user("Ada", Some(""), Some(&["a@x"]));
    check!(r#"name "Ada", nickname "", emails ["a@x"]"#, handles(&u), vec!["Ada", "", "a@x"]);
}

#[test]
fn add_email_appends_to_an_empty_list() {
    let mut u = user("Ada", None, Some(&[]));
    add_email(&mut u, "a@x".to_string());
    check!(r#"emails = Some([]), add "a@x""#, u.emails, Some(vec!["a@x".to_string()]));
}

#[test]
fn add_email_keeps_existing() {
    let mut u = user("Ada", None, Some(&["a@x"]));
    add_email(&mut u, "b@y".to_string());
    check!(r#"emails = ["a@x"], add "b@y""#, (primary_email(&u).map(str::to_string), u.emails.as_ref().map(Vec::len)), (Some("a@x".to_string()), Some(2)));
}

#[test]
fn add_email_moves_the_string() {
    let mut u = user("Ada", None, None);
    let e = String::from("a@x");
    let p = e.as_ptr();
    add_email(&mut u, e);
    check!(r#"add an email and keep its buffer"#, u.emails.as_ref().map(|es| es[0].as_ptr()), Some(p));
}

#[test]
fn shout_none() {
    let mut u = user("Ada", None, None);
    shout_nickname(&mut u);
    check!(r#"no nickname"#, (u.nickname, u.name), (None, "Ada".to_string()));
}

#[test]
fn shout_mixed_and_unicode() {
    let mut u = user("x", Some("a1-bC é"), None);
    shout_nickname(&mut u);
    check!(r#"nickname "a1-bC é""#, u.nickname, Some("A1-BC é".to_string()));
}

#[test]
fn shout_twice() {
    let mut u = user("x", Some("ace"), None);
    shout_nickname(&mut u);
    shout_nickname(&mut u);
    check!(r#"nickname "ace", shouted twice"#, u.nickname, Some("ACE".to_string()));
}

#[test]
fn display_name_borrows() {
    let u = user("Ada", Some("ace"), None);
    let v = user("Ada", None, None);
    check!(r#"nickname "ace", and none"#, (std::ptr::eq(display_name(&u).as_ptr(), u.nickname.as_ref().unwrap().as_ptr()), std::ptr::eq(display_name(&v).as_ptr(), v.name.as_ptr())), (true, true));
}

#[test]
fn primary_email_borrows() {
    let u = user("Ada", None, Some(&["a@x"]));
    check!(r#"emails ["a@x"]"#, std::ptr::eq(primary_email(&u).unwrap().as_ptr(), u.emails.as_ref().unwrap()[0].as_ptr()), true);
}

#[test]
fn handles_borrow() {
    let u = user("Ada", Some("ace"), Some(&["a@x"]));
    let hs = handles(&u);
    check!(r#"name "Ada", nickname "ace", emails ["a@x"]"#, hs.iter().zip([u.name.as_ptr(), u.nickname.as_ref().unwrap().as_ptr(), u.emails.as_ref().unwrap()[0].as_ptr()]).all(|(h, p)| std::ptr::eq(h.as_ptr(), p)), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7104);
    for _ in 0..300 {
        let len = rng.below(4);
        let name = rng.string(len, "abZ ");
        let nickname = if rng.bool() {
            let len = rng.below(4);
            Some(rng.string(len, "xyQ!é"))
        } else {
            None
        };
        let emails: Option<Vec<String>> = if rng.bool() {
            let n = rng.below(3);
            Some((0..n).map(|i| format!("e{i}@x")).collect())
        } else {
            None
        };
        let mut u = User { name: name.clone(), nickname: nickname.clone(), emails: emails.clone() };
        let desc = format!("name = {name:?}, nickname = {nickname:?}, emails = {emails:?}");
        let mut want: Vec<String> = vec![name.clone()];
        if let Some(n) = &nickname {
            want.push(n.clone());
        }
        if let Some(es) = &emails {
            want.extend(es.iter().cloned());
        }
        check!(format!("display_name, {desc}"), display_name(&u).to_string(), nickname.clone().unwrap_or(name.clone()));
        check!(format!("primary_email, {desc}"), primary_email(&u).map(str::to_string), emails.as_ref().and_then(|es| es.first().cloned()));
        check!(format!("handles, {desc}"), handles(&u).iter().map(|h| h.to_string()).collect::<Vec<_>>(), want);
        shout_nickname(&mut u);
        add_email(&mut u, "new@x".to_string());
        let mut es = emails.clone().unwrap_or_default();
        es.push("new@x".to_string());
        check!(format!("shout + add_email, {desc}"), (u.nickname, u.emails, u.name), (nickname.map(|n| n.to_ascii_uppercase()), Some(es), name));
    }
}

#[test]
fn scale_many_emails() {
    let mut u = user("Ada", Some("ace"), None);
    for i in 0..200_000 {
        add_email(&mut u, format!("{i}@x"));
    }
    let hs = handles(&u);
    check!("200000 add_email calls, then handles", (hs.len(), hs[2], hs[200_001], primary_email(&u)), (200_002, "0@x", "199999@x", Some("0@x")));
}
