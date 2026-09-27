use solution::*;

#[test]
fn none() {
    check!(r#"items [1], limit 40"#, { let mut s = Shop::new(vec![1]); s.log_expensive(40); s.log().len() }, 0);
}
