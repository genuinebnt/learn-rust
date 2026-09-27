use solution::*;

#[test]
fn same_length() {
    check!(r#"["b", "a", "c"]"#, { let mut w: Vec<String> = ["b", "a", "c"].map(String::from).to_vec(); by_len_then_alpha(&mut w); w }, vec!["a", "b", "c"]);
}
