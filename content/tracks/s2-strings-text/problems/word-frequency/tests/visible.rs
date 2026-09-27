use solution::*;

#[test]
fn counts() {
    check!(r#""The cat. the DOG!\ncat""#, word_frequencies("The cat. the DOG!\ncat".as_bytes()).unwrap(), vec![("cat".to_string(), 2), ("the".to_string(), 2), ("dog".to_string(), 1)]);
}

#[test]
fn empty() {
    check!(r#""""#, word_frequencies("".as_bytes()).unwrap().len(), 0);
}

#[test]
fn leetcode_692_first() {
    check!(r#""i love leetcode i love coding""#, word_frequencies("i love leetcode i love coding".as_bytes()).unwrap(), vec![("i".to_string(), 2), ("love".to_string(), 2), ("coding".to_string(), 1), ("leetcode".to_string(), 1)]);
}

#[test]
fn leetcode_692_second() {
    check!(r#""the day is sunny the the the sunny is is""#, word_frequencies("the day is sunny the the the sunny is is".as_bytes()).unwrap(), vec![("the".to_string(), 4), ("is".to_string(), 3), ("sunny".to_string(), 2), ("day".to_string(), 1)]);
}

#[test]
fn punctuation_stripped() {
    check!(r#""(hi) hi! HI""#, word_frequencies("(hi) hi! HI".as_bytes()).unwrap(), vec![("hi".to_string(), 3)]);
}
