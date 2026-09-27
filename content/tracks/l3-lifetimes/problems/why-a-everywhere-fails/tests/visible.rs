use solution::*;

#[test]
fn first_outlives_sep() {
    let text = String::from("a,b,c");
    let first;
    {
        let sep = String::from(",");
        first = Splitter::new(&text, &sep).first();
    }
    check!(r#"text "a,b,c", separator dropped"#, first, "a");
}

#[test]
fn parts_outlive_sep() {
    let text = String::from("a--b");
    let parts;
    {
        let sep = String::from("--");
        parts = Splitter::new(&text, &sep).parts();
    }
    check!(r#"text "a--b", separator dropped"#, parts, vec!["a", "b"]);
}
