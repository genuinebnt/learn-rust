use solution::*;

#[test]
fn leetcode_three() {
    check!(r#"nums = [1, 5, 2]"#, predict_the_winner(&[1, 5, 2]), false);
}

#[test]
fn leetcode_four() {
    check!(r#"nums = [1, 5, 233, 7]"#, predict_the_winner(&[1, 5, 233, 7]), true);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, predict_the_winner(&[]), true);
}

#[test]
fn single() {
    check!(r#"nums = [5]"#, predict_the_winner(&[5]), true);
}

#[test]
fn tie_counts_as_a_win() {
    check!(r#"nums = [1, 1]"#, predict_the_winner(&[1, 1]), true);
}
