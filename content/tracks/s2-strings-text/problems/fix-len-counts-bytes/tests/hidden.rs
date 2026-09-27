use solution::*;

#[test]
fn odd() {
    check!(r#""abc", 6, '-'"#, center("abc", 6, '-'), "-abc--".to_string());
}

#[test]
fn too_wide() {
    check!(r#""日本語", 3, ' '"#, center("日本語", 3, ' '), "日本語".to_string());
}

#[test]
fn multibyte_fill() {
    check!(r#""x", 3, '·'"#, center("x", 3, '·'), "·x·".to_string());
}

#[test]
fn empty() {
    check!(r#""", 3, 'x'"#, center("", 3, 'x'), "xxx".to_string());
}

#[test]
fn width_zero() {
    check!(r#""ab", 0, '*'"#, center("ab", 0, '*'), "ab".to_string());
}

#[test]
fn emoji() {
    check!(r#""🦀", 3, '.'"#, center("🦀", 3, '.'), ".🦀.".to_string());
}

#[test]
fn cjk() {
    check!(r#""日本", 6, ' '"#, center("日本", 6, ' '), "  日本  ".to_string());
}

#[test]
fn fits_in_chars_not_bytes() {
    check!(r#""éé", 3, '.'"#, center("éé", 3, '.'), "éé.".to_string());
}

#[test]
fn inner_spaces() {
    check!(r#""a b", 5, '*'"#, center("a b", 5, '*'), "*a b*".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2210);
    for _ in 0..300 {
        let len = rng.below(6);
        let s = rng.string(len, "a é日");
        let width = rng.below(10);
        let fill = *rng.pick(&['*', '·']);
        let n = s.chars().count();
        let mut want = String::new();
        if n >= width {
            want.push_str(&s);
        } else {
            let left = (width - n) / 2;
            for _ in 0..left {
                want.push(fill);
            }
            want.push_str(&s);
            for _ in 0..width - n - left {
                want.push(fill);
            }
        }
        check!(format!("s = {s:?}, width = {width}, fill = {fill:?}"), center(&s, width, fill), want);
    }
}
