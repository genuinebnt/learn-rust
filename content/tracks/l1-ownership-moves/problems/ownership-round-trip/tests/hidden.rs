use solution::*;

#[test]
fn no_limit() {
    let mut out = Outbox::new();
    check!(r#"new(), push 10000 bytes"#, (out.push("x".repeat(10_000)), out.remaining() > 1_000_000), (Ok(()), true));
}

#[test]
fn limit_zero_empty_message() {
    let mut out = Outbox::new().limit(0);
    check!(r#"limit 0, push "" then "a""#, (out.push(String::new()), out.push("a".into())), (Ok(()), Err("a".to_string())));
}

#[test]
fn reject_keeps_budget() {
    let mut out = Outbox::new().limit(4);
    check!(r#"limit 4, push "abcde" (rejected) then "abcd""#, (out.push("abcde".into()), out.push("abcd".into()), out.remaining()), (Err("abcde".to_string()), Ok(()), 0));
}

#[test]
fn bytes_not_chars() {
    let mut out = Outbox::new().limit(4);
    check!(r#"limit 4, push "日本" (6 bytes) then "é" (2 bytes)"#, (out.push("日本".into()), out.push("é".into()), out.remaining()), (Err("日本".to_string()), Ok(()), 2));
}

#[test]
fn valid_but_too_big_bytes_come_back() {
    let mut out = Outbox::new().limit(1);
    let raw = b"ok".to_vec();
    let ptr = raw.as_ptr();
    let err = out.push_bytes(raw);
    let same = err.as_ref().err().map(|b| b.as_ptr()) == Some(ptr);
    check!(r#"limit 1, push_bytes(b"ok")"#, (err, same), (Err(b"ok".to_vec()), true));
}

#[test]
fn truncated_utf8() {
    let mut out = Outbox::new();
    check!(r#"push_bytes of "é" missing its last byte"#, out.push_bytes(vec![0xc3]), Err(vec![0xc3]));
}

#[test]
fn order_kept() {
    let mut out = Outbox::new();
    out.push("a".into()).unwrap();
    out.push_bytes(b"b".to_vec()).unwrap();
    out.push("c".into()).unwrap();
    check!(r#"push "a", push_bytes(b"b"), push "c""#, out.into_messages(), vec!["a", "b", "c"]);
}

#[test]
fn messages_are_the_pushed_strings() {
    let mut out = Outbox::new();
    let s = String::from("mine");
    let ptr = s.as_ptr();
    out.push(s).unwrap();
    let msgs = out.into_messages();
    check!(r#"into_messages returns the pushed String itself"#, msgs[0].as_ptr() == ptr, true);
}

#[test]
fn empty_outbox() {
    check!(r#"new().into_messages()"#, Outbox::new().into_messages(), Vec::<String>::new());
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6104);
    for _ in 0..300 {
        let limit = rng.below(12);
        let mut out = Outbox::new().limit(limit);
        let (mut used, mut kept) = (0usize, Vec::new());
        let mut ops = Vec::new();
        for _ in 0..rng.below(8) {
            let len = rng.below(5);
            let mut raw = rng.string(len, "aé").into_bytes();
            if rng.below(4) == 0 && !raw.is_empty() {
                raw.pop();
            }
            ops.push(format!("push_bytes({raw:?})"));
            let fits = match std::str::from_utf8(&raw) {
                Ok(s) if s.len() <= limit - used => Some(s.to_string()),
                _ => None,
            };
            let want = match &fits {
                Some(_) => Ok(()),
                None => Err(raw.clone()),
            };
            if let Some(s) = fits {
                used += s.len();
                kept.push(s);
            }
            check!(format!("limit {limit}, {ops:?}"), out.push_bytes(raw), want);
        }
        check!(format!("limit {limit}, {ops:?}, remaining"), out.remaining(), limit - used);
        check!(format!("limit {limit}, {ops:?}, into_messages"), out.into_messages(), kept);
    }
}

#[test]
fn many_messages() {
    let mut out = Outbox::new().limit(1_000_000);
    for i in 0..200_000 {
        let _ = out.push(format!("{}", i % 10));
    }
    check!("200000 one-byte messages", (out.remaining(), out.into_messages().len()), (800_000, 200_000));
}
