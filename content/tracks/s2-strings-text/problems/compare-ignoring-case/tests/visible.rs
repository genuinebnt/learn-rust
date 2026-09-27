use solution::*;

#[test]
fn command_matches() {
    check!(r#""  QUIT \n", "quit""#, is_command("  QUIT \n", "quit"), true);
}

#[test]
fn prefix_is_not_the_command() {
    check!(r#""quitter", "quit""#, is_command("quitter", "quit"), false);
}

#[test]
fn header_lowercased() {
    let mut h = String::from("Content-Type");
    normalize_header(&mut h);
    check!(r#""Content-Type""#, h, "content-type".to_string());
}

#[test]
fn title_accented() {
    check!(r#""ÉCOLE maternelle""#, title_case("ÉCOLE maternelle"), "École Maternelle".to_string());
}

#[test]
fn title_sharp_s_expands() {
    check!(r#""ßig""#, title_case("ßig"), "SSig".to_string());
}
