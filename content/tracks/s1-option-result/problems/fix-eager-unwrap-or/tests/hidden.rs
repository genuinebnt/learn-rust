use solution::*;

#[test]
fn empty_choice_is_still_a_choice() {
    check!(r#"chosen = Some(""), palette = ["blue"]"#, (theme(Some(""), &["blue"]), theme_len(Some(""), &["blue"])), ("", 0));
}

#[test]
fn single_colour() {
    check!(r#"chosen = None, palette = ["teal"]"#, (theme(None, &["teal"]), theme_len(None, &["teal"])), ("teal", 4));
}

#[test]
fn chosen_black() {
    check!(r#"chosen = Some("black"), palette = []"#, (theme(Some("black"), &[]), theme_len(Some("black"), &[])), ("black", 5));
}

#[test]
fn chosen_in_palette() {
    check!(r#"chosen = Some("green"), palette = ["blue", "green"]"#, theme(Some("green"), &["blue", "green"]), "green");
}

#[test]
fn empty_first_colour() {
    check!(r#"chosen = None, palette = ["", "blue"]"#, (theme(None, &["", "blue"]), theme_len(None, &["", "blue"])), ("", 0));
}

#[test]
fn unicode_choice_empty_palette() {
    check!(r#"chosen = Some("青"), palette = []"#, (theme(Some("青"), &[]), theme_len(Some("青"), &[])), ("青", 3));
}

#[test]
fn unicode_palette_length_in_bytes() {
    check!(r#"chosen = None, palette = ["rosé", "青"]"#, (theme(None, &["rosé", "青"]), theme_len(None, &["rosé", "青"])), ("rosé", 5));
}

#[test]
fn empty_choice_empty_palette() {
    check!(r#"chosen = Some(""), palette = []"#, (theme(Some(""), &[]), theme_len(Some(""), &[])), ("", 0));
}

#[test]
fn returns_the_chosen_str() {
    let c = "crimson";
    check!(r#"chosen = Some(c), palette = []"#, std::ptr::eq(theme(Some(c), &[]).as_ptr(), c.as_ptr()), true);
}

#[test]
fn long_palette() {
    let names: Vec<String> = (0..100_000).map(|i| format!("c{i}")).collect();
    let palette: Vec<&str> = names.iter().map(|s| s.as_str()).collect();
    check!(r#"chosen = None, palette = 100000 colours"#, (theme(None, &palette), theme_len(None, &palette)), ("c0", 2));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1312);
    let colours = ["red", "blue", "", "black", "青"];
    for _ in 0..300 {
        let chosen = if rng.bool() { Some(*rng.pick(&colours)) } else { None };
        let n = rng.below(4);
        let mut palette: Vec<&str> = Vec::new();
        for _ in 0..n {
            palette.push(*rng.pick(&colours));
        }
        let want = match (chosen, palette.first()) {
            (Some(c), _) => Some(c),
            (None, Some(&p)) => Some(p),
            (None, None) => None,
        };
        let desc = format!("chosen = {chosen:?}, palette = {palette:?}");
        check!(format!("theme, {desc}"), theme(chosen, &palette), want.unwrap_or("black"));
        check!(format!("theme_len, {desc}"), theme_len(chosen, &palette), want.map_or(0, str::len));
    }
}
