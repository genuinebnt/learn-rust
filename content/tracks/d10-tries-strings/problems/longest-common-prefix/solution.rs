pub fn longest_common_prefix<'a>(strs: &[&'a str]) -> &'a str {
    let Some((&first, rest)) = strs.split_first() else {
        return "";
    };
    let mut prefix = first;
    for s in rest {
        // Byte length of the shared characters, so the cut is always on a char boundary.
        let len: usize = prefix.chars().zip(s.chars()).take_while(|(a, b)| a == b).map(|(a, _)| a.len_utf8()).sum();
        prefix = &prefix[..len];
    }
    prefix
}
