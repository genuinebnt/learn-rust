use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn leetcode_six() {
    check!(r#"num = "123", target = 6"#, sorted(add_operators("123", 6)), vec!["1*2*3", "1+2+3"]);
}

#[test]
fn leetcode_precedence() {
    check!(r#"num = "232", target = 8"#, sorted(add_operators("232", 8)), vec!["2*3+2", "2+3*2"]);
}

#[test]
fn leetcode_none() {
    check!(r#"num = "3456237490", target = 9191"#, add_operators("3456237490", 9191), Vec::<String>::new());
}

#[test]
fn leetcode_no_leading_zero() {
    check!(r#"num = "105", target = 5 ("1*05" is not allowed)"#, sorted(add_operators("105", 5)), vec!["1*0+5", "10-5"]);
}

#[test]
fn leetcode_zeros() {
    check!(r#"num = "00", target = 0"#, sorted(add_operators("00", 0)), vec!["0*0", "0+0", "0-0"]);
}

#[test]
fn no_operator() {
    check!(r#"num = "123", target = 123"#, add_operators("123", 123), vec!["123"]);
}
