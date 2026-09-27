use solution::*;

#[test]
fn leetcode_28() {
    check!(r#"nums = [3, 10, 5, 25, 2, 8]"#, find_maximum_xor(&[3, 10, 5, 25, 2, 8]), 28);
}

#[test]
fn leetcode_127() {
    check!(r#"nums = [14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70]"#, find_maximum_xor(&[14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70]), 127);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, find_maximum_xor(&[]), 0);
}

#[test]
fn single() {
    check!(r#"nums = [7]"#, find_maximum_xor(&[7]), 0);
}

#[test]
fn best_pair_skips_the_max() {
    check!(r#"nums = [6, 5, 3] (5 ^ 3 = 6 beats anything with 6)"#, find_maximum_xor(&[6, 5, 3]), 6);
}

#[test]
fn top_bit_counts() {
    check!(r#"nums = [2147483648, 1] (2³¹ and 1)"#, find_maximum_xor(&[1 << 31, 1]), (1 << 31) | 1);
}
