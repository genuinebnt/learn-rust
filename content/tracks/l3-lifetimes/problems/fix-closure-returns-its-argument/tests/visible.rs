use solution::*;

#[test]
fn trimmed_lines_example() {
    check!(r#"trimmed_lines("  a \n\n b")"#, trimmed_lines("  a \n\n b"), vec!["a", "b"]);
}

#[test]
fn first_fields_example() {
    check!(r#"first_fields("a,b\nc\n,d")"#, first_fields("a,b\nc\n,d"), vec!["a", "c", ""]);
}

#[test]
fn comment_stripper_example() {
    check!(r###"comment_stripper().run("## note ")"###, comment_stripper().run("## note "), "note");
}

#[test]
fn results_borrow_the_input() {
    let t = String::from("x,y");
    check!(r#"first_fields' result points into the text"#, first_fields(&t)[0].as_ptr() == t.as_ptr(), true);
}

#[test]
fn pipeline_result_outlives_pipeline() {
    let s = String::from("# kept");
    let out = comment_stripper().run(&s);
    check!(r#"run a dropped pipeline's steps on a String"#, out, "kept");
}
