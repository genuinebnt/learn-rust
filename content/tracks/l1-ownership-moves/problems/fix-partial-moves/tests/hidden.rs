use solution::*;

use std::cell::Cell;
use std::rc::Rc;

#[test]
fn describe_empty_body() {
    check!(r#"describe with Some(empty body)"#, describe(&Request { id: 6, method: "get".to_string(), path: "/".to_string(), headers: vec![], body: Some(b"".to_vec()) }), "6 get / (0 headers, 0 bytes)");
}

#[test]
fn describe_many_headers() {
    check!(r#"describe with 3 headers"#, describe(&Request { id: 7, method: "get".to_string(), path: "/h".to_string(), headers: vec![("a".to_string(), "1".to_string()), ("b".to_string(), "2".to_string()), ("c".to_string(), "3".to_string())], body: Some(b"xy".to_vec()) }), "7 get /h (3 headers, 2 bytes)");
}

#[test]
fn first_content_type_wins() {
    check!(r#"two content-type headers"#, route(Request { id: 8, method: "post".to_string(), path: "/u".to_string(), headers: vec![("content-type".to_string(), "a".to_string()), ("CONTENT-TYPE".to_string(), "b".to_string())], body: None }).content_type, Some("a".to_string()));
}

#[test]
fn no_content_type() {
    check!(r#"no content-type header"#, route(Request { id: 9, method: "get".to_string(), path: "/n".to_string(), headers: vec![("content-length".to_string(), "0".to_string())], body: None }).content_type, None);
}

#[test]
fn similar_header_name() {
    check!(r#""content-type-x" isn't "content-type""#, route(Request { id: 10, method: "get".to_string(), path: "/s".to_string(), headers: vec![("content-type-x".to_string(), "v".to_string())], body: None }).content_type, None);
}

#[test]
fn route_no_body() {
    check!(r#"route without a body"#, route(Request { id: 11, method: "head".to_string(), path: "/e".to_string(), headers: vec![], body: None }), Routed { id: 11, route: "HEAD /e".to_string(), content_type: None, body: vec![], trace: "11 head /e (0 headers, 0 bytes)".to_string() });
}

#[test]
fn method_upper_ascii_and_unicode() {
    check!(r#"method "pAtch", path "/日本""#, route(Request { id: 12, method: "pAtch".to_string(), path: "/日本".to_string(), headers: vec![], body: None }).route, "PATCH /日本");
}

#[test]
fn pooled_full_result() {
    let slots = Rc::new(Cell::new(0));
    let r = route_pooled(Pooled { req: Request { id: 13, method: "post".to_string(), path: "/z".to_string(), headers: vec![], body: Some(b"q".to_vec()) }, free_slots: Rc::clone(&slots) });
    check!(r#"route_pooled of post /z with a body"#, r, Routed { id: 13, route: "POST /z".to_string(), content_type: None, body: b"q".to_vec(), trace: "13 post /z (0 headers, 1 bytes)".to_string() });
}

#[test]
fn pooled_body_not_copied() {
    let q = Request { id: 14, method: "put".to_string(), path: "/q".to_string(), headers: vec![], body: Some(b"data".to_vec()) };
    let ptr = q.body.as_ref().unwrap().as_ptr();
    let r = route_pooled(Pooled { req: q, free_slots: Rc::new(Cell::new(0)) });
    check!(r#"route_pooled keeps the body buffer"#, r.body.as_ptr() == ptr, true);
}

#[test]
fn pool_rc_released() {
    let slots = Rc::new(Cell::new(0));
    let _ = route_pooled(Pooled { req: Request { id: 15, method: "get".to_string(), path: "/r".to_string(), headers: vec![], body: None }, free_slots: Rc::clone(&slots) });
    check!(r#"route_pooled drops its handle on the pool"#, Rc::strong_count(&slots), 1);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6112);
    for _ in 0..300 {
        let id = rng.below(1000) as u64;
        let ml = rng.below(4);
        let method = rng.string(ml, "gEt");
        let pl = rng.below(4);
        let path = format!("/{}", rng.string(pl, "ab"));
        let k = rng.below(4);
        let mut headers = Vec::new();
        for _ in 0..k {
            let name = rng.pick(&["content-type", "Content-Type", "host", "accept"]).to_string();
            let vl = rng.below(3);
            headers.push((name, rng.string(vl, "xy")));
        }
        let body = if rng.bool() { let n = rng.below(5); Some(rng.vec::<u8>(n, 0, 255)) } else { None };
        let trace = format!("{id} {method} {path} ({} headers, {} bytes)", headers.len(), body.as_ref().map_or(0, |b| b.len()));
        let content_type = headers.iter().find(|(k, _)| k.to_ascii_lowercase() == "content-type").map(|(_, v)| v.clone());
        let want = Routed { id, route: format!("{} {path}", method.to_uppercase()), content_type, body: body.clone().unwrap_or_default(), trace };
        let r = Request { id, method, path, headers, body };
        let input = format!("{r:?}");
        let slots = Rc::new(Cell::new(0));
        let got = if rng.bool() { route(r) } else { route_pooled(Pooled { req: r, free_slots: Rc::clone(&slots) }) };
        check!(input, got, want);
    }
}
