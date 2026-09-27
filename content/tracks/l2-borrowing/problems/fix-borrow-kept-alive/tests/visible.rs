use solution::*;

#[test]
fn new_document() {
    check!(r#"out = [], items = ["apples", "kiwi"]"#, { let mut out = Vec::<String>::new(); let items: [&str; 2] = ["apples", "kiwi"]; let n = render(&mut out, &items); (n, out) }, (4, vec!["untitled".to_string(), "- apples".to_string(), "- kiwi".to_string(), "2 items, longest: apples".to_string()]));
}

#[test]
fn continues_a_title() {
    check!(r#"out = ["Shopping"], items = ["milk"]"#, { let mut out = vec!["Shopping".to_string()]; let items: [&str; 1] = ["milk"]; let n = render(&mut out, &items); (n, out) }, (3, vec!["Shopping (cont.)".to_string(), "- milk".to_string(), "1 items, longest: milk".to_string()]));
}

#[test]
fn no_items() {
    check!(r#"out = [], items = []"#, { let mut out = Vec::<String>::new(); let items: [&str; 0] = []; let n = render(&mut out, &items); (n, out) }, (2, vec!["untitled".to_string(), "0 items, longest: -".to_string()]));
}

#[test]
fn first_longest_wins() {
    check!(r#"out = [], items = ["ab", "cd", "e"]"#, { let mut out = Vec::<String>::new(); let items: [&str; 3] = ["ab", "cd", "e"]; let n = render(&mut out, &items); (n, out) }, (5, vec!["untitled".to_string(), "- ab".to_string(), "- cd".to_string(), "- e".to_string(), "3 items, longest: ab".to_string()]));
}

#[test]
fn keeps_earlier_lines() {
    check!(r#"out = ["T", "- x", "1 items, longest: x"], items = ["yy"]"#, { let mut out = vec!["T".to_string(), "- x".to_string(), "1 items, longest: x".to_string()]; let items: [&str; 1] = ["yy"]; let n = render(&mut out, &items); (n, out) }, (5, vec!["T (cont.)".to_string(), "- x".to_string(), "1 items, longest: x".to_string(), "- yy".to_string(), "1 items, longest: yy".to_string()]));
}

#[test]
fn longest_is_by_bytes() {
    check!(r#"out = [], items = ["ééé", "abcd"]"#, { let mut out = Vec::<String>::new(); let items: [&str; 2] = ["ééé", "abcd"]; let n = render(&mut out, &items); (n, out) }, (4, vec!["untitled".to_string(), "- ééé".to_string(), "- abcd".to_string(), "2 items, longest: ééé".to_string()]));
}
