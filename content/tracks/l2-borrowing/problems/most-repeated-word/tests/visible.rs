use solution::*;

#[test]
fn example() {
    check!(r#"text = "the cat and the hat and the bat", k = 2"#, top_words("the cat and the hat and the bat", 2), vec![("the", 3), ("and", 2)]);
}

#[test]
fn case_folds_to_first_spelling() {
    check!(r#"text = "Rust rust RUST go Go", k = 5"#, top_words("Rust rust RUST go Go", 5), vec![("Rust", 3), ("go", 2)]);
}

#[test]
fn tie_goes_to_first_seen() {
    check!(r#"text = "b a a b c", k = 3"#, top_words("b a a b c", 3), vec![("b", 2), ("a", 2), ("c", 1)]);
}

#[test]
fn punctuation_splits() {
    check!(r#"text = "well-known, well: known!", k = 2"#, top_words("well-known, well: known!", 2), vec![("well", 2), ("known", 2)]);
}

#[test]
fn k_beyond_distinct() {
    check!(r#"text = "x y", k = 10"#, top_words("x y", 10), vec![("x", 1), ("y", 1)]);
}

#[test]
fn empty_text() {
    check!(r#"text = "", k = 3"#, top_words("", 3), Vec::<(&str, usize)>::new());
}

#[test]
fn k_zero() {
    check!(r#"text = "a a", k = 0"#, top_words("a a", 0), Vec::<(&str, usize)>::new());
}
