use solution::*;

#[test]
fn logs() {
    check!(r#"items [5, 50, 500], limit 40"#, { let mut s = Shop::new(vec![5, 50, 500]); s.log_expensive(40); s.log().to_vec() }, vec!["expensive: 50", "expensive: 500"]);
}

#[test]
fn at_limit() {
    check!(r#"items [40], limit 40"#, { let mut s = Shop::new(vec![40]); s.log_expensive(40); s.log().len() }, 0);
}
