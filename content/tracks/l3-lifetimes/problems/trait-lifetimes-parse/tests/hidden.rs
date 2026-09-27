use solution::*;

#[test]
fn fields_borrow_the_line() {
    let line = String::from("ab,cd");
    check!(r#"fields::<&str> results point into the line"#, fields::<&str>(&line).unwrap()[1].as_ptr() == line[3..].as_ptr(), true);
}

#[test]
fn fields_bad_number() {
    check!(r#"fields::<u32>("1,x")"#, fields::<u32>("1,x"), None);
}

#[test]
fn fields_empty_line() {
    check!(r#"fields::<&str>("")"#, fields::<&str>(""), Some(vec![""]));
}

#[test]
fn pair_second_equals_in_value() {
    check!(r#"fields::<Pair>("k=a=b")"#, fields::<Pair>("k=a=b"), Some(vec![Pair { key: "k", value: "a=b" }]));
}

#[test]
fn pair_empty_parts() {
    check!(r#"fields::<Pair>(" = ")"#, fields::<Pair>(" = "), Some(vec![Pair { key: "", value: "" }]));
}

#[test]
fn read_owned_empty() {
    check!(r#"read_owned::<u32>("")"#, read_owned::<u32>("".as_bytes()), None);
}

#[test]
fn read_owned_crlf() {
    check!(r#"read_owned::<u32>("7\r\n")"#, read_owned::<u32>("7\r\n".as_bytes()), Some(7));
}

#[test]
fn fields_strings_owned() {
    let v = { let line = String::from("a, b"); fields::<String>(&line) };
    check!(r#"fields::<String>("a, b") outlive the line"#, v, Some(vec!["a".to_string(), "b".to_string()]));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6315);
    for _ in 0..300 {
        let len = rng.below(12);
        let line = rng.string(len, "ab =,");
        let want: Option<Vec<(String, String)>> = line
            .split(',')
            .map(|f| f.split_once('=').map(|(k, v)| (k.trim().to_string(), v.trim().to_string())))
            .collect();
        let got = fields::<Pair>(&line).map(|v| v.into_iter().map(|p| (p.key.to_string(), p.value.to_string())).collect::<Vec<_>>());
        check!(format!("fields::<Pair>({line:?})"), got, want);
        let want: Vec<&str> = line.split(',').map(str::trim).collect();
        check!(format!("fields::<&str>({line:?})"), fields::<&str>(&line), Some(want));
    }
}
