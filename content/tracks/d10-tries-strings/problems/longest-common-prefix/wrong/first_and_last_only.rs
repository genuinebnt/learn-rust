pub fn longest_common_prefix<'a>(strs: &[&'a str]) -> &'a str {
    let (Some(&first), Some(&last)) = (strs.first(), strs.last()) else {
        return "";
    };
    let len: usize = first.chars().zip(last.chars()).take_while(|(a, b)| a == b).map(|(a, _)| a.len_utf8()).sum();
    &first[..len]
}
