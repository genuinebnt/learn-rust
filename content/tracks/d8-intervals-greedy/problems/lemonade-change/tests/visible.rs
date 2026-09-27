use solution::*;

#[test]
fn leetcode_yes() {
    check!(r#"bills = [5, 5, 5, 10, 20]"#, lemonade_change(&[5, 5, 5, 10, 20]), true);
}

#[test]
fn leetcode_no() {
    check!(r#"bills = [5, 5, 10, 10, 20]"#, lemonade_change(&[5, 5, 10, 10, 20]), false);
}

#[test]
fn no_customers() {
    check!(r#"bills = []"#, lemonade_change(&[]), true);
}

#[test]
fn first_pays_ten() {
    check!(r#"bills = [10]"#, lemonade_change(&[10]), false);
}

#[test]
fn three_fives_for_twenty() {
    check!(r#"bills = [5, 5, 5, 20]"#, lemonade_change(&[5, 5, 5, 20]), true);
}

#[test]
fn give_the_ten_first() {
    check!(r#"bills = [5, 5, 5, 5, 10, 20, 10, 10]"#, lemonade_change(&[5, 5, 5, 5, 10, 20, 10, 10]), true);
}
