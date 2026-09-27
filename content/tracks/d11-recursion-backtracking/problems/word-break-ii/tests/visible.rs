use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn leetcode_cats_and_dog() {
    check!(r#"s = "catsanddog", word_dict = ["cat", "cats", "and", "sand", "dog"]"#, sorted(word_break("catsanddog", &["cat", "cats", "and", "sand", "dog"])), vec!["cat sand dog", "cats and dog"]);
}

#[test]
fn leetcode_pineapple() {
    check!(r#"s = "pineapplepenapple", word_dict = ["apple", "pen", "applepen", "pine", "pineapple"]"#, sorted(word_break("pineapplepenapple", &["apple", "pen", "applepen", "pine", "pineapple"])), vec!["pine apple pen apple", "pine applepen apple", "pineapple pen apple"]);
}

#[test]
fn leetcode_no_sentence() {
    check!(r#"s = "catsandog", word_dict = ["cats", "dog", "sand", "and", "cat"]"#, word_break("catsandog", &["cats", "dog", "sand", "and", "cat"]), Vec::<String>::new());
}

#[test]
fn word_used_twice() {
    check!(r#"s = "dogdog", word_dict = ["dog"]"#, word_break("dogdog", &["dog"]), vec!["dog dog"]);
}

#[test]
fn whole_string_is_a_word() {
    check!(r#"s = "apple", word_dict = ["apple", "app", "le"]"#, sorted(word_break("apple", &["apple", "app", "le"])), vec!["app le", "apple"]);
}

#[test]
fn repeated_dictionary_word() {
    check!(r#"s = "catcat", word_dict = ["cat", "cat"]"#, word_break("catcat", &["cat", "cat"]), vec!["cat cat"]);
}
