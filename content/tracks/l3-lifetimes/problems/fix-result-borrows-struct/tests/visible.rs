use solution::*;

#[test]
fn longest_line_outlives_index() {
    let text = String::from("fn main\nlet x\nfn helper\n");
    let l = Index::new(&text).longest_line();
    check!(r#"let text = String::from("fn main\nlet x\nfn helper\n"); longest_line, then drop the index"#, l, "fn helper");
}

#[test]
fn lines_with() {
    let text = String::from("fn main\nlet x\nfn helper\n");
    let v = Index::new(&text).lines_with("fn");
    check!(r#"lines containing "fn", after the index is dropped"#, v, vec!["fn main", "fn helper"]);
}

#[test]
fn iter_items_outlive_index() {
    let text = String::from("fn main\nlet x\nfn helper\n");
    let v: Vec<&str> = {
        let ix = Index::new(&text);
        ix.iter().collect()
    };
    check!(r#"collect iter() into a Vec, drop the index"#, v, vec!["fn main", "let x", "fn helper"]);
}

#[test]
fn into_lines() {
    let text = String::from("fn main\nlet x\nfn helper\n");
    check!(r#"into_lines"#, Index::new(&text).into_lines(), vec!["fn main", "let x", "fn helper"]);
}

#[test]
fn lines_with_temporary_word() {
    let text = String::from("fn main\nlet x\nfn helper\n");
    let ix = Index::new(&text);
    let v = ix.lines_with(&String::from("x"));
    check!(r#"lines_with a word that's dropped first"#, v, vec!["let x"]);
}
