use solution::*;

#[test]
fn run_macros_example() {
    let mut e = Editor::new("banana");
    e.macros = vec![Macro::Append("!".to_string()), Macro::Replace("a".to_string(), "o".to_string()), Macro::Upper];
    e.run_macros();
    e.run_macros();
    check!(r#"text "banana"; macros [Append "!", Replace "a" with "o", Upper]; run twice"#, (e.text.as_str(), e.log().to_vec(), e.macros.len()), ("BONONO!!", ["1. append !", "2. replace a with o", "3. upper", "4. append !", "5. replace a with o", "6. upper"].map(String::from).to_vec(), 3));
}

#[test]
fn cut_then_paste_twice() {
    let mut e = Editor::new("hi");
    e.cut();
    e.paste();
    e.paste();
    check!(r#"text "hi"; cut; paste; paste"#, (e.text.as_str(), e.clipboard.as_str(), e.log().to_vec()), ("hihi", "hi", ["1. cut 2 bytes", "2. paste hi", "3. paste hi"].map(String::from).to_vec()));
}

#[test]
fn cut_moves_the_text() {
    let mut e = Editor::new("moved");
    let p = e.text.as_ptr();
    e.cut();
    check!(r#"text "moved"; cut"#, (p == e.clipboard.as_ptr(), e.text.is_empty()), (true, true));
}

#[test]
fn no_macros() {
    let mut e = Editor::new("x");
    e.run_macros();
    check!(r#"text "x"; run_macros"#, (e.text.as_str(), e.log().len()), ("x", 0));
}

#[test]
fn paste_empty_clipboard() {
    let mut e = Editor::new("a");
    e.paste();
    check!(r#"text "a"; paste"#, (e.text.as_str(), e.log().to_vec()), ("a", vec!["1. paste ".to_string()]));
}
