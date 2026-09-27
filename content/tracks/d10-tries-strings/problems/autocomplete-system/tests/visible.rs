use solution::*;

fn typed(sys: &mut AutocompleteSystem, keys: &str) -> Vec<Vec<String>> {
    keys.chars().map(|c| sys.input(c)).collect()
}

#[test]
fn leetcode_type_i() {
    let mut sys = AutocompleteSystem::new(&["i love you", "island", "iroman", "i love leetcode"], &[5, 3, 2, 2]);
    check!(r#"sentences = ["i love you", "island", "iroman", "i love leetcode"], times = [5, 3, 2, 2]; type "i""#, typed(&mut sys, "i"), vec![vec!["i love you", "island", "i love leetcode"]]);
}

#[test]
fn leetcode_type_i_space() {
    let mut sys = AutocompleteSystem::new(&["i love you", "island", "iroman", "i love leetcode"], &[5, 3, 2, 2]);
    check!(r#"LeetCode's system; type "i", " ""#, typed(&mut sys, "i "), vec![vec!["i love you", "island", "i love leetcode"], vec!["i love you", "i love leetcode"]]);
}

#[test]
fn leetcode_type_i_space_a() {
    let mut sys = AutocompleteSystem::new(&["i love you", "island", "iroman", "i love leetcode"], &[5, 3, 2, 2]);
    check!(r#"LeetCode's system; type "i", " ", "a" (nothing starts with "i a")"#, typed(&mut sys, "i a"), vec![vec!["i love you", "island", "i love leetcode"], vec!["i love you", "i love leetcode"], vec![]]);
}

#[test]
fn leetcode_type_i_space_a_hash() {
    let mut sys = AutocompleteSystem::new(&["i love you", "island", "iroman", "i love leetcode"], &[5, 3, 2, 2]);
    check!(r##"LeetCode's system; type "i", " ", "a", "#" ('#' returns nothing)"##, typed(&mut sys, "i a#"), vec![vec!["i love you", "island", "i love leetcode"], vec!["i love you", "i love leetcode"], vec![], vec![]]);
}

#[test]
fn hash_saves_the_sentence() {
    let mut sys = AutocompleteSystem::new(&["i love you", "island", "iroman", "i love leetcode"], &[5, 3, 2, 2]);
    typed(&mut sys, "i a#");
    check!(r#"LeetCode's system; type "i a#", then "i " ("i a" now has count 1)"#, typed(&mut sys, "i "), vec![vec!["i love you", "island", "i love leetcode"], vec!["i love you", "i love leetcode", "i a"]]);
}

#[test]
fn ties_in_ascii_order() {
    let mut sys = AutocompleteSystem::new(&["ab", "a b", "aa"], &[1, 1, 1]);
    check!(r#"sentences = ["ab", "a b", "aa"], times = [1, 1, 1]; type "a" (space sorts first)"#, typed(&mut sys, "a"), vec![vec!["a b", "aa", "ab"]]);
}

#[test]
fn typing_makes_a_sentence_hotter() {
    let mut sys = AutocompleteSystem::new(&["cat", "car", "cow", "cub"], &[1, 1, 1, 1]);
    typed(&mut sys, "cub#");
    check!(r#"sentences = ["cat", "car", "cow", "cub"], times = [1, 1, 1, 1]; type "cub#", then "c""#, typed(&mut sys, "c"), vec![vec!["cub", "car", "cat"]]);
}
