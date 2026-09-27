use solution::*;

use std::cell::Cell;
use std::rc::Rc;

#[test]
fn describe_borrows() {
    let r = Request { id: 1, method: "get".to_string(), path: "/a".to_string(), headers: vec![], body: Some(b"abc".to_vec()) };
    check!(r#"describe(&req), then use req"#, (describe(&r), r.path), ("1 get /a (0 headers, 3 bytes)".to_string(), "/a".to_string()));
}

#[test]
fn describe_no_body() {
    check!(r#"describe of a request without a body"#, describe(&Request { id: 2, method: "post".to_string(), path: "/b".to_string(), headers: vec![("x".to_string(), "y".to_string())], body: None }), "2 post /b (1 headers, 0 bytes)");
}

#[test]
fn route_all_fields() {
    check!(r#"route(get /x, content-type json, body "{}")"#, route(Request { id: 3, method: "get".to_string(), path: "/x".to_string(), headers: vec![("Host".to_string(), "h".to_string()), ("Content-Type".to_string(), "json".to_string())], body: Some(b"{}".to_vec()) }), Routed { id: 3, route: "GET /x".to_string(), content_type: Some("json".to_string()), body: b"{}".to_vec(), trace: "3 get /x (2 headers, 2 bytes)".to_string() });
}

#[test]
fn route_body_not_copied() {
    let q = Request { id: 4, method: "put".to_string(), path: "/p".to_string(), headers: vec![], body: Some(b"hello".to_vec()) };
    let ptr = q.body.as_ref().unwrap().as_ptr();
    let r = route(q);
    check!(r#"route keeps the request's body buffer"#, (r.body.as_ptr() == ptr, r.body.len()), (true, 5));
}

#[test]
fn pooled_gives_slot_back() {
    let slots = Rc::new(Cell::new(0));
    let r = route_pooled(Pooled { req: Request { id: 5, method: "delete".to_string(), path: "/d".to_string(), headers: vec![], body: None }, free_slots: Rc::clone(&slots) });
    check!(r#"route_pooled, then check the pool"#, (r.route, slots.get()), ("DELETE /d".to_string(), 1));
}
