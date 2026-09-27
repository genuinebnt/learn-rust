use solution::*;

#[test]
fn empty_text() {
    check!(r#"decode_normalized::<u32>("")"#, decode_normalized::<u32>(""), Vec::<Option<u32>>::new());
}

#[test]
fn empty_line_is_empty_list() {
    check!(r#"decode_normalized::<Vec<u32>>("\n1")"#, decode_normalized::<Vec<u32>>("\n1"), vec![Some(vec![]), Some(vec![1])]);
}

#[test]
fn uppercase_unicode() {
    check!(r#"decode_normalized::<String>("ÉTÉ")"#, decode_normalized::<String>("ÉTÉ"), vec![Some("été".to_string())]);
}

#[test]
fn u32_overflow() {
    check!(r#"decode_normalized::<u32>("4294967296")"#, decode_normalized::<u32>("4294967296"), vec![None]);
}

#[test]
fn u32_max() {
    check!(r#"decode_normalized::<u32>("4294967295")"#, decode_normalized::<u32>("4294967295"), vec![Some(u32::MAX)]);
}

#[test]
fn lines_unchanged() {
    check!(r#"decode_lines::<String>(" A ")"#, decode_lines::<String>(" A "), vec![Some(" A ".to_string())]);
}

#[test]
fn borrowed_empty_line() {
    check!(r#"decode_lines::<&str>("a\n\nb")"#, decode_lines::<&str>("a\n\nb"), vec![Some("a"), None, Some("b")]);
}

#[test]
fn borrowed_list() {
    check!(r#"decode_lines::<Vec<&str>>("x,y")"#, decode_lines::<Vec<&str>>("x,y"), vec![Some(vec!["x", "y"])]);
}

#[test]
fn list_with_empty_item() {
    check!(r#"decode_normalized::<Vec<u32>>("1,,2")"#, decode_normalized::<Vec<u32>>("1,,2"), vec![None]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4420);
    for _ in 0..300 {
        let n = rng.below(4);
        let lines: Vec<String> = (0..n).map(|_| {
            let pad = rng.below(2);
            let body = if rng.below(5) == 0 { "X".to_string() } else { rng.int(0, 999).to_string() };
            format!("{}{}{}", " ".repeat(pad), body, " ".repeat(pad))
        }).collect();
        let text = lines.join("\n");
        let want: Vec<Option<u32>> = lines.iter().map(|l| l.trim().to_lowercase().parse().ok()).collect();
        check!(format!("{text:?}"), decode_normalized::<u32>(&text), want);
    }
}
