use solution::*;

#[test]
fn closure_route() {
    let r = Router::default().route("/up", |req: &str| req.to_uppercase());
    check!(r#"route /up to |req| req.to_uppercase(); dispatch /up "hi""#, r.dispatch("/up", "hi"), "HI");
}

#[test]
fn function_route() {
    fn len_of(req: &str) -> String {
        req.len().to_string()
    }
    let r = Router::default().route("/len", len_of);
    check!(r#"route /len to fn len_of"#, r.dispatch("/len", "four"), "4");
}

#[test]
fn shared_dyn_handler() {
    let h: Arc<dyn Handler + Send + Sync> = Arc::new(Static("ok".into()));
    let r = Router::default().route("/a", h.clone()).route("/b", h);
    check!(r#"one Arc<dyn Handler> on /a and /b"#, (r.dispatch("/a", ""), r.dispatch("/b", "")), ("ok".to_string(), "ok".to_string()));
}

#[test]
fn describe_through_arc() {
    let r = Router::default().route("/s", Arc::new(Static("x".into()))).route("/f", |_: &str| String::new());
    check!(r#"routes /s (Arc<Static>), /f (closure)"#, r.describe(), vec!["/f: handler", "/s: static"]);
}

#[test]
fn not_found() {
    check!(r#"dispatch /nope on an empty router"#, Router::default().dispatch("/nope", ""), "404 /nope");
}

use std::sync::Arc;
