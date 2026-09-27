use solution::*;

#[test]
fn five() {
    check!(r#"begin = "hit", end = "cog", words = ["hot","dot","dog","lot","log","cog"]"#, ladder_length("hit", "cog", &["hot", "dot", "dog", "lot", "log", "cog"]), 5);
}

#[test]
fn end_missing() {
    check!(r#"begin = "hit", end = "cog", words = ["hot","dot","dog","lot","log"]"#, ladder_length("hit", "cog", &["hot", "dot", "dog", "lot", "log"]), 0);
}
