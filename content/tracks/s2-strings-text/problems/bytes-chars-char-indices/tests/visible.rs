use solution::*;

#[test]
fn line_and_column() {
    check!(r#""ab\ncdé\nf", at 7 and 8"#, (line_col("ab\ncdé\nf", 7), line_col("ab\ncdé\nf", 8)), (Some((2, 4)), Some((3, 1))));
}

#[test]
fn inside_a_char() {
    check!(r#""héllo", 2"#, line_col("héllo", 2), None);
}

#[test]
fn char_to_byte_and_end() {
    check!(r#""héllo", n = 2, 5, 6"#, (char_to_byte("héllo", 2), char_to_byte("héllo", 5), char_to_byte("héllo", 6)), (Some(3), Some(6), None));
}

#[test]
fn matches_do_not_overlap() {
    check!(r#""aaaa", "aa""#, find_all("aaaa", "aa"), vec![(0, 0), (2, 2)]);
}

#[test]
fn byte_and_char_offsets() {
    check!(r#""é-é-é", "é""#, find_all("é-é-é", "é"), vec![(0, 0), (3, 2), (6, 4)]);
}
