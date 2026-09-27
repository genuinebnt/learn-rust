The tests register plain closures (`|req: &str| req.to_uppercase()`), functions, boxed closures, `Arc`s of
handlers and `Arc<dyn Handler + Send + Sync>` shared by several routes. None of those is a `Handler` yet.
Add blanket impls so they all are, without changing `Router`. `describe` must show the real handler's
name through an `Arc`.
