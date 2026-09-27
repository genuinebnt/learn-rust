use solution::*;

#[test]
fn plain_row() {
    check!(r#"["a", "b", "c"]"#, csv_row(&["a", "b", "c"]), "a,b,c".to_string());
}

#[test]
fn comma_is_quoted() {
    check!(r#""b,c""#, csv_field("b,c"), "\"b,c\"".to_string());
}

#[test]
fn quote_is_doubled() {
    check!(r#""say \"hi\"""#, csv_field("say \"hi\""), "\"say \"\"hi\"\"\"".to_string());
}

#[test]
fn empty_first_field() {
    check!(r#"["", "x"]"#, csv_row(&["", "x"]), ",x".to_string());
}

#[test]
fn no_fields() {
    check!(r#"[]"#, csv_row(&[]), String::new());
}
