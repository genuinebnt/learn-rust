use solution::*;

#[test]
fn one() {
    let input = String::from("x");
    check!(r#"input "x" from a String"#, all_names(&input).len(), 3);
}

#[test]
fn crlf() {
    check!(r#""a\r\nb""#, all_names("a\r\nb"), vec!["a", "b", "root", "admin"]);
}

#[test]
fn root_already_there() {
    check!(r#""root""#, all_names("root"), vec!["root", "root", "admin"]);
}

#[test]
fn unicode() {
    check!(r#""émile\nzoë""#, all_names("émile\nzoë"), vec!["émile", "zoë", "root", "admin"]);
}

#[test]
fn spaces_kept() {
    check!(r#"" a ""#, all_names(" a "), vec![" a ", "root", "admin"]);
}

#[test]
fn names_point_into_input() {
    let input = String::from("bob");
    let names = all_names(&input);
    check!(r#"first name points into the String"#, std::ptr::eq(names[0].as_ptr(), input.as_ptr()), true);
}

#[test]
fn defaults_last() {
    let input: String = (0..1000).map(|i| format!("n{i}\n")).collect();
    let names = all_names(&input);
    check!(r#"1000 names"#, (names.len(), names[999], names[1000], names[1001]), (1002, "n999", "root", "admin"));
}

#[test]
fn only_newlines() {
    check!(r#""\n\n""#, all_names("\n\n"), vec!["", "", "root", "admin"]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(316);
    for _ in 0..300 {
        let n = rng.below(10);
        let input = rng.string(n, "ab\n");
        let mut want: Vec<&str> = input.split('\n').collect();
        if input.is_empty() || input.ends_with('\n') {
            want.pop();
        }
        want.push("root");
        want.push("admin");
        check!(format!("input = {input:?}"), all_names(&input), want);
    }
}
