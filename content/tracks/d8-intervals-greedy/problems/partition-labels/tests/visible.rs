use solution::*;

#[test]
fn leetcode_three_pieces() {
    check!(r#"s = "ababcbacadefegdehijhklij""#, partition_labels("ababcbacadefegdehijhklij"), vec![9, 7, 8]);
}

#[test]
fn leetcode_one_piece() {
    check!(r#"s = "eccbbbbdec""#, partition_labels("eccbbbbdec"), vec![10]);
}

#[test]
fn empty() {
    check!(r#"s = """#, partition_labels(""), Vec::<usize>::new());
}

#[test]
fn single() {
    check!(r#"s = "a""#, partition_labels("a"), vec![1]);
}

#[test]
fn all_distinct() {
    check!(r#"s = "abc""#, partition_labels("abc"), vec![1, 1, 1]);
}

#[test]
fn repeat_joins_everything() {
    check!(r#"s = "abca""#, partition_labels("abca"), vec![4]);
}
