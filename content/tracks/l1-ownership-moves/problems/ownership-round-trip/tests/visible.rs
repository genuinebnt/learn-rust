use solution::*;

#[test]
fn builder_and_push() {
    let mut out = Outbox::new().limit(10);
    let ok = (out.push("hello".to_string()), out.push("world".to_string()));
    check!(r#"new().limit(10), push "hello" and "world""#, (ok, out.remaining(), out.into_messages()), ((Ok(()), Ok(())), 0, vec!["hello".to_string(), "world".to_string()]));
}

#[test]
fn rejected_string_comes_back() {
    let mut out = Outbox::new().limit(3);
    let msg = String::from("toolong");
    let ptr = msg.as_ptr();
    let err = out.push(msg);
    let same = err.as_ref().err().map(|m| m.as_ptr()) == Some(ptr);
    check!(r#"limit 3, push "toolong""#, (err, same, out.remaining()), (Err("toolong".to_string()), true, 3));
}

#[test]
fn invalid_utf8_comes_back() {
    let mut out = Outbox::new();
    let raw = vec![0xff, b'a'];
    let ptr = raw.as_ptr();
    let err = out.push_bytes(raw);
    let same = err.as_ref().err().map(|b| b.as_ptr()) == Some(ptr);
    check!(r#"push_bytes([0xff, b'a'])"#, (err, same), (Err(vec![0xff, b'a']), true));
}

#[test]
fn valid_bytes_reuse_buffer() {
    let mut out = Outbox::new();
    let raw = b"hi".to_vec();
    let ptr = raw.as_ptr();
    let ok = out.push_bytes(raw);
    let msgs = out.into_messages();
    check!(r#"push_bytes(b"hi"), then into_messages"#, (ok, msgs[0].as_str(), msgs[0].as_ptr() == ptr), (Ok(()), "hi", true));
}

#[test]
fn exactly_fits() {
    let mut out = Outbox::new().limit(5);
    check!(r#"limit 5, push "abc" then "de" then "f""#, (out.push("abc".into()), out.push("de".into()), out.push("f".into())), (Ok(()), Ok(()), Err("f".to_string())));
}
