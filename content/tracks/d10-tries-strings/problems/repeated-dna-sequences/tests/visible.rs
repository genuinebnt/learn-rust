use solution::*;

#[test]
fn leetcode_two_sequences() {
    check!(r#"s = "AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT", k = 10"#, find_repeated_dna_sequences("AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT", 10), vec!["AAAAACCCCC", "CCCCCAAAAA"]);
}

#[test]
fn leetcode_overlapping() {
    check!(r#"s = "AAAAAAAAAAAAA", k = 10 (four overlapping copies, reported once)"#, find_repeated_dna_sequences("AAAAAAAAAAAAA", 10), vec!["AAAAAAAAAA"]);
}

#[test]
fn k_longer_than_s() {
    check!(r#"s = "ACGT", k = 10"#, find_repeated_dna_sequences("ACGT", 10), Vec::<&str>::new());
}

#[test]
fn empty() {
    check!(r#"s = "", k = 1"#, find_repeated_dna_sequences("", 1), Vec::<&str>::new());
}

#[test]
fn order_of_first_appearance() {
    check!(r#"s = "ACGTCGAC", k = 2 (AC first appears before CG, though CG repeats sooner)"#, find_repeated_dna_sequences("ACGTCGAC", 2), vec!["AC", "CG"]);
}

#[test]
fn single_letters() {
    check!(r#"s = "AAAAAA", k = 1"#, find_repeated_dna_sequences("AAAAAA", 1), vec!["A"]);
}
