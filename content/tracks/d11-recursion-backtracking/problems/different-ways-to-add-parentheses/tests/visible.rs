use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn leetcode_two_minus_one_minus_one() {
    check!(r#"expression = "2-1-1""#, sorted(diff_ways_to_compute("2-1-1")), vec![0, 2]);
}

#[test]
fn leetcode_mixed() {
    check!(r#"expression = "2*3-4*5""#, sorted(diff_ways_to_compute("2*3-4*5")), vec![-34, -14, -10, -10, 10]);
}

#[test]
fn single_number() {
    check!(r#"expression = "7""#, diff_ways_to_compute("7"), vec![7]);
}

#[test]
fn duplicates_are_kept() {
    check!(r#"expression = "1+1+1" (two groupings, same value)"#, diff_ways_to_compute("1+1+1"), vec![3, 3]);
}

#[test]
fn two_digit_numbers() {
    check!(r#"expression = "10-5*2""#, sorted(diff_ways_to_compute("10-5*2")), vec![0, 10]);
}
