use solution::*;

#[test]
fn newline_is_quoted() {
    check!(r#""a\nb""#, csv_field("a\nb"), "\"a\nb\"".to_string());
}

#[test]
fn carriage_return_is_quoted() {
    check!(r#""a\rb""#, csv_field("a\rb"), "\"a\rb\"".to_string());
}

#[test]
fn lone_quote() {
    check!(r#""\"""#, csv_field("\""), "\"\"\"\"".to_string());
}

#[test]
fn plain_field_unchanged() {
    check!(r#""hello world""#, csv_field("hello world"), "hello world".to_string());
}

#[test]
fn empty_field() {
    check!(r#""""#, csv_field(""), String::new());
}

#[test]
fn all_empty_fields() {
    check!(r#"["", "", ""]"#, csv_row(&["", "", ""]), ",,".to_string());
}

#[test]
fn one_empty_field() {
    check!(r#"[""]"#, csv_row(&[""]), String::new());
}

#[test]
fn mixed_row() {
    check!(r#"["id", "a,b", "", "x\"y"]"#, csv_row(&["id", "a,b", "", "x\"y"]), "id,\"a,b\",,\"x\"\"y\"".to_string());
}

#[test]
fn unicode_fields() {
    check!(r#"["café", "日本,語"]"#, csv_row(&["café", "日本,語"]), "café,\"日本,語\"".to_string());
}

#[test]
fn single_quote_not_special() {
    check!(r#""it's""#, csv_field("it's"), "it's".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7203);
    for _ in 0..400 {
        let n = rng.below(5);
        let mut fields = Vec::new();
        for _ in 0..n {
            let len = rng.below(4);
            fields.push(rng.string(len, "a,\"\né "));
        }
        let mut want = String::new();
        for (i, f) in fields.iter().enumerate() {
            if i > 0 {
                want.push(',');
            }
            if f.chars().any(|c| c == ',' || c == '"' || c == '\n' || c == '\r') {
                want.push('"');
                for c in f.chars() {
                    if c == '"' {
                        want.push('"');
                    }
                    want.push(c);
                }
                want.push('"');
            } else {
                want.push_str(f);
            }
        }
        let refs: Vec<&str> = fields.iter().map(|f| f.as_str()).collect();
        check!(format!("fields = {fields:?}"), csv_row(&refs), want);
    }
}

#[test]
fn scale_100k_fields() {
    let fields = vec!["a\"b"; 100_000];
    let row = csv_row(&fields);
    check!("fields = [\"a\\\"b\"; 100000]", (row.len(), &row[..13]), (100_000 * 7 - 1, "\"a\"\"b\",\"a\"\"b\""));
}
