use solution::*;

#[test]
fn leetcode_cattle() {
    check!(r#"roots = ["cat", "bat", "rat"], sentence = "the cattle was rattled by the battery""#, replace_words(&["cat", "bat", "rat"], "the cattle was rattled by the battery"), "the cat was rat by the bat");
}

#[test]
fn leetcode_single_letters() {
    check!(r#"roots = ["a", "b", "c"], sentence = "aadsfasf absbs bbab cadsfafs""#, replace_words(&["a", "b", "c"], "aadsfasf absbs bbab cadsfafs"), "a a b c");
}

#[test]
fn shortest_root_wins() {
    check!(r#"roots = ["cat", "ca"], sentence = "cattle""#, replace_words(&["cat", "ca"], "cattle"), "ca");
}

#[test]
fn no_roots() {
    check!(r#"roots = [], sentence = "hello world""#, replace_words(&[], "hello world"), "hello world");
}

#[test]
fn empty_sentence() {
    check!(r#"roots = ["a"], sentence = """#, replace_words(&["a"], ""), "");
}

#[test]
fn root_longer_than_word() {
    check!(r#"roots = ["catalog"], sentence = "cat""#, replace_words(&["catalog"], "cat"), "cat");
}
