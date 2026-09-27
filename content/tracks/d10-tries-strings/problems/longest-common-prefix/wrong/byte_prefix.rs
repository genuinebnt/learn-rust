pub fn longest_common_prefix<'a>(strs: &[&'a str]) -> &'a str {
    let Some((&first, rest)) = strs.split_first() else {
        return "";
    };
    let mut prefix = first;
    for s in rest {
        let len = prefix.bytes().zip(s.bytes()).take_while(|(a, b)| a == b).count();
        prefix = &prefix[..len];
    }
    prefix
}
