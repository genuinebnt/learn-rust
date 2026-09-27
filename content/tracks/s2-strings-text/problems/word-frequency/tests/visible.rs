use solution::*;

#[test]
fn counts() {
    check!(r#""The cat. the DOG!\ncat""#, word_frequencies("The cat. the DOG!\ncat".as_bytes()).unwrap(), vec![("cat".to_string(), 2), ("the".to_string(), 2), ("dog".to_string(), 1)]);
}

#[test]
fn empty() {
    check!(r#""""#, word_frequencies("".as_bytes()).unwrap().len(), 0);
}
