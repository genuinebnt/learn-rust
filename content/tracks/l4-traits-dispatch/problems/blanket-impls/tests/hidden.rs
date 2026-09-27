use solution::*;

#[test]
fn boxed_closure() {
    let r = Router::default().route("/b", Box::new(|req: &str| format!("{req}!")));
    check!(r#"route a Box<closure>"#, r.dispatch("/b", "x"), "x!");
}

#[test]
fn closure_captures_arc_counter() {
    let hits = Arc::new(std::sync::atomic::AtomicUsize::new(0));
    let h2 = hits.clone();
    let r = Router::default().route("/c", move |_: &str| {
        h2.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
        String::new()
    });
    for _ in 0..3 {
        r.dispatch("/c", "");
    }
    check!(r#"closure counting calls; 3 dispatches"#, hits.load(std::sync::atomic::Ordering::SeqCst), 3);
}

#[test]
fn arc_of_closure() {
    let r = Router::default().route("/a", Arc::new(|req: &str| format!("<{req}>")));
    check!(r#"Arc::new(closure)"#, r.dispatch("/a", "q"), "<q>");
}

#[test]
fn describe_dyn_arc() {
    let h: Arc<dyn Handler + Send + Sync> = Arc::new(Static(String::new()));
    let r = Router::default().route("/x", h);
    check!(r#"Arc<dyn Handler> of a Static"#, r.describe(), vec!["/x: static"]);
}

#[test]
fn nested_arc() {
    let r = Router::default().route("/n", Arc::new(Arc::new(Static("deep".into()))));
    check!(r#"Arc<Arc<Static>>"#, (r.dispatch("/n", ""), r.describe()), ("deep".to_string(), vec!["/n: static".to_string()]));
}

#[test]
fn replaced_route() {
    let r = Router::default().route("/r", Static("first".into())).route("/r", Static("second".into()));
    check!(r#"route /r twice"#, r.dispatch("/r", ""), "second");
}

#[test]
fn unicode_request() {
    let r = Router::default().route("/rev", |req: &str| req.chars().rev().collect::<String>());
    check!(r#"closure echoing the request reversed"#, r.dispatch("/rev", "héllo"), "olléh");
}

#[test]
fn dispatch_from_threads() {
    let r = Router::default().route("/up", |req: &str| req.to_uppercase());
    let mut out: Vec<String> = std::thread::scope(|s| {
        let hs: Vec<_> = ["a", "b", "c", "d"].iter().map(|q| {
            let r = &r;
            s.spawn(move || r.dispatch("/up", q))
        }).collect();
        hs.into_iter().map(|h| h.join().unwrap()).collect()
    });
    out.sort();
    check!(r#"4 threads dispatch /up"#, out, vec!["A", "B", "C", "D"]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4419);
    for _ in 0..200 {
        let reps = rng.below(3);
        let tag = rng.string(2, "xy");
        let t2 = tag.clone();
        let shared: Arc<dyn Handler + Send + Sync> = Arc::new(Static(tag.clone()));
        let r = Router::default()
            .route("/rep", move |req: &str| req.repeat(reps))
            .route("/tag", move |req: &str| format!("{t2}{req}"))
            .route("/s1", shared.clone())
            .route("/s2", shared);
        let len = rng.below(4);
        let req = rng.string(len, "ab");
        check!(format!("/rep x{reps} {req:?}"), r.dispatch("/rep", &req), req.repeat(reps));
        check!(format!("/tag {tag:?} {req:?}"), r.dispatch("/tag", &req), format!("{tag}{req}"));
        check!(format!("/s1 and /s2 = {tag:?}"), (r.dispatch("/s1", &req), r.dispatch("/s2", &req)), (tag.clone(), tag.clone()));
    }
}

use std::sync::Arc;
