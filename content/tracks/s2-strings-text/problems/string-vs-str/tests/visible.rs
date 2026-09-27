use solution::*;

#[test]
fn extension_last_dot() {
    check!(r#""src/archive.tar.gz""#, extension("src/archive.tar.gz"), Some("gz"));
}

#[test]
fn dotfile_has_no_extension() {
    check!(r#"".bashrc""#, extension(".bashrc"), None);
}

#[test]
fn unquote_one_pair() {
    check!(r#""\"hi\"" and "'hi'""#, (unquote("\"hi\""), unquote("'hi'")), ("hi", "hi"));
}

#[test]
fn first_param() {
    let mut u = String::from("http://h/p");
    add_param(&mut u, "k", "v");
    check!(r#"url = "http://h/p", key = "k", value = "v""#, u, "http://h/p?k=v".to_string());
}

#[test]
fn param_before_fragment() {
    let mut u = String::from("http://h/p?a=1#top");
    add_param(&mut u, "k", "v");
    check!(r#"url = "http://h/p?a=1#top", key = "k", value = "v""#, u, "http://h/p?a=1&k=v#top".to_string());
}
