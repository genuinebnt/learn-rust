use solution::*;

#[test]
fn logs() {
    check!(r#"items [5, 50, 500], limit 40"#, { let mut s = Shop::new(vec![5, 50, 500]); s.log_expensive(40); s.log().to_vec() }, vec!["expensive: 50", "expensive: 500"]);
}

#[test]
fn at_limit() {
    check!(r#"items [40], limit 40"#, { let mut s = Shop::new(vec![40]); s.log_expensive(40); s.log().len() }, 0);
}

#[test]
fn order() {
    check!(r#"items [9, 1, 8], limit 5"#, { let mut s = Shop::new(vec![9, 1, 8]); s.log_expensive(5); s.log().to_vec() }, vec!["expensive: 9", "expensive: 8"]);
}

#[test]
fn empty_items() {
    check!(r#"items [], limit 0"#, { let mut s = Shop::new(vec![]); s.log_expensive(0); s.log().len() }, 0);
}

#[test]
fn none() {
    check!(r#"items [1], limit 40"#, { let mut s = Shop::new(vec![1]); s.log_expensive(40); s.log().len() }, 0);
}
