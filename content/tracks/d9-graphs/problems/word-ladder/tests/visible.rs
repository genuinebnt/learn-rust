use solution::*;

#[test]
fn five() {
    check!(r#"begin = "hit", end = "cog", words = ["hot","dot","dog","lot","log","cog"]"#, ladder_length("hit", "cog", &["hot", "dot", "dog", "lot", "log", "cog"]), 5);
}

#[test]
fn end_missing() {
    check!(r#"begin = "hit", end = "cog", words = ["hot","dot","dog","lot","log"]"#, ladder_length("hit", "cog", &["hot", "dot", "dog", "lot", "log"]), 0);
}

#[test]
fn counts_words_not_steps() {
    check!(r#"begin = "hot", end = "dot", words = ["dot"]"#, ladder_length("hot", "dot", &["dot"]), 2);
}

#[test]
fn begin_may_be_listed() {
    check!(r#"begin = "hot", end = "dog", words = ["hot","dot","dog"]"#, ladder_length("hot", "dog", &["hot", "dot", "dog"]), 3);
}

#[test]
fn two_letters_at_once_is_not_a_step() {
    check!(r#"begin = "hit", end = "cog", words = ["hot","cog"]"#, ladder_length("hit", "cog", &["hot", "cog"]), 0);
}
