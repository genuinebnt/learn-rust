use solution::*;

fn rules(xs: &[(&str, &[&str])]) -> std::collections::HashMap<String, Vec<String>> {
    xs.iter().map(|(k, v)| (k.to_string(), v.iter().map(|s| s.to_string()).collect())).collect()
}

fn run(tasks: &[&str], r: &[(&str, &[&str])]) -> (usize, Vec<String>) {
    let mut t: Vec<String> = tasks.iter().map(|s| s.to_string()).collect();
    let n = expand(&mut t, &rules(r));
    (n, t)
}

#[test]
fn example() {
    check!(r#"tasks ["build"], rules {"build": ["compile", "test"], "test": ["lint"]}"#, run(&["build"], &[("build", &["compile", "test"][..]), ("test", &["lint"][..])]), (3, ["build", "compile", "test", "lint"].map(String::from).to_vec()));
}

#[test]
fn nothing_to_expand() {
    check!(r#"tasks ["a", "b"], rules {"c": ["d"]}"#, run(&["a", "b"], &[("c", &["d"][..])]), (0, ["a", "b"].map(String::from).to_vec()));
}

#[test]
fn already_listed() {
    check!(r#"tasks ["a", "b"], rules {"a": ["b", "c"]}"#, run(&["a", "b"], &[("a", &["b", "c"][..])]), (1, ["a", "b", "c"].map(String::from).to_vec()));
}

#[test]
fn cycle() {
    check!(r#"tasks ["a"], rules {"a": ["b"], "b": ["a", "c"]}"#, run(&["a"], &[("a", &["b"][..]), ("b", &["a", "c"][..])]), (2, ["a", "b", "c"].map(String::from).to_vec()));
}

#[test]
fn empty_tasks() {
    check!(r#"tasks [], rules {"a": ["b"]}"#, run(&[], &[("a", &["b"][..])]), (0, Vec::<String>::new()));
}
