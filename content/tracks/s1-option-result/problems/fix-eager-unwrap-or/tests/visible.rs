use solution::*;

#[test]
fn chosen_wins() {
    check!(r#"chosen = Some("red"), palette = ["blue", "green"]"#, (theme(Some("red"), &["blue", "green"]), theme_len(Some("red"), &["blue", "green"])), ("red", 3));
}

#[test]
fn first_of_palette() {
    check!(r#"chosen = None, palette = ["blue", "green"]"#, (theme(None, &["blue", "green"]), theme_len(None, &["blue", "green"])), ("blue", 4));
}

#[test]
fn nothing_at_all() {
    check!(r#"chosen = None, palette = []"#, (theme(None, &[]), theme_len(None, &[])), ("black", 0));
}

#[test]
fn theme_with_empty_palette() {
    check!(r#"chosen = Some("red"), palette = []"#, theme(Some("red"), &[]), "red");
}

#[test]
fn theme_len_with_empty_palette() {
    check!(r#"chosen = Some("red"), palette = []"#, theme_len(Some("red"), &[]), 3);
}
