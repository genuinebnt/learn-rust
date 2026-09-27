use solution::*;

#[test]
fn one_letter_repeated() {
    check!(r#"s = "aaaa""#, partition_labels("aaaa"), vec![4]);
}

#[test]
fn two_blocks() {
    check!(r#"s = "aabb""#, partition_labels("aabb"), vec![2, 2]);
}

#[test]
fn nested() {
    check!(r#"s = "abba""#, partition_labels("abba"), vec![4]);
}

#[test]
fn crossing() {
    check!(r#"s = "abab""#, partition_labels("abab"), vec![4]);
}

#[test]
fn tail_piece() {
    check!(r#"s = "abac""#, partition_labels("abac"), vec![3, 1]);
}

#[test]
fn head_piece() {
    check!(r#"s = "caedbdedda""#, partition_labels("caedbdedda"), vec![1, 9]);
}

#[test]
fn alphabet() {
    check!(r#"s = "abcdefghijklmnopqrstuvwxyz""#, partition_labels("abcdefghijklmnopqrstuvwxyz"), vec![1; 26]);
}

#[test]
fn mixed() {
    check!(r#"s = "qiejxqfnqceocmy""#, partition_labels("qiejxqfnqceocmy"), vec![13, 1, 1]);
}

#[test]
fn first_and_last() {
    check!(r#"s = "zaz""#, partition_labels("zaz"), vec![3]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(817);
    for _ in 0..400 {
        let len = rng.below(13);
        let s = rng.string(len, "abcd");
        // A cut after p is allowed when no letter appears on both sides.
        let b = s.as_bytes();
        let mut want = Vec::new();
        let mut start = 0;
        for p in 1..=b.len() {
            if p == b.len() || b[..p].iter().all(|c| !b[p..].contains(c)) {
                want.push(p - start);
                start = p;
            }
        }
        check!(format!("s = {s:?}"), partition_labels(&s), want);
    }
}

#[test]
fn scale_200k() {
    let mut s = "abcdefghijklmnopqrstuvwxy".repeat(4_000);
    s.push_str(&"z".repeat(100_000));
    let sizes = partition_labels(&s);
    check!("'abc…y' × 4000, then 100000 'z's", sizes, vec![100_000, 100_000]);
}
