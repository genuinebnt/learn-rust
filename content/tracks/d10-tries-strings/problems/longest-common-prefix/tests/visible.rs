use solution::*;

#[test]
fn leetcode_flower() {
    check!(r#"strs = ["flower", "flow", "flight"]"#, longest_common_prefix(&["flower", "flow", "flight"]), "fl");
}

#[test]
fn leetcode_no_prefix() {
    check!(r#"strs = ["dog", "racecar", "car"]"#, longest_common_prefix(&["dog", "racecar", "car"]), "");
}

#[test]
fn empty_list() {
    check!(r#"strs = []"#, longest_common_prefix(&[]), "");
}

#[test]
fn single_string() {
    check!(r#"strs = ["alone"]"#, longest_common_prefix(&["alone"]), "alone");
}

#[test]
fn empty_string_inside() {
    check!(r#"strs = ["abc", ""]"#, longest_common_prefix(&["abc", ""]), "");
}

#[test]
fn whole_word_is_the_prefix() {
    check!(r#"strs = ["ab", "abc", "abcd"]"#, longest_common_prefix(&["ab", "abc", "abcd"]), "ab");
}

#[test]
fn unicode_characters() {
    check!(r#"strs = ["héllo", "hélium"]"#, longest_common_prefix(&["héllo", "hélium"]), "hél");
}
