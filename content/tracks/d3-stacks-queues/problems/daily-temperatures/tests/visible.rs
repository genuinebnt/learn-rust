use solution::*;

#[test]
fn example() {
    check!(r#"[73,74,75,71,69,72,76,73]"#, daily_temperatures(&[73, 74, 75, 71, 69, 72, 76, 73]), vec![1, 1, 4, 2, 1, 1, 0, 0]);
}

#[test]
fn rising() {
    check!(r#"[30,40,50,60]"#, daily_temperatures(&[30, 40, 50, 60]), vec![1, 1, 1, 0]);
}

#[test]
fn three() {
    check!(r#"[30,60,90]"#, daily_temperatures(&[30, 60, 90]), vec![1, 1, 0]);
}

#[test]
fn falling() {
    check!(r#"[60,50,40]"#, daily_temperatures(&[60, 50, 40]), vec![0, 0, 0]);
}

#[test]
fn equal_is_not_warmer() {
    check!(r#"[50,50,51]"#, daily_temperatures(&[50, 50, 51]), vec![2, 1, 0]);
}
