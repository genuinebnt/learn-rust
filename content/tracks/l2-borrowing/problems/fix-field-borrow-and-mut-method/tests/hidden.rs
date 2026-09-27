use solution::*;

#[test]
fn cut_replaces_clipboard() {
    let mut e = Editor::new("one");
    e.cut();
    e.text.push_str("two");
    e.cut();
    check!(r#"text "one"; cut; text = "two"; cut"#, (e.clipboard.as_str(), e.text.as_str()), ("two", ""));
}

#[test]
fn cut_empty() {
    let mut e = Editor::new("");
    e.cut();
    check!(r#"text ""; cut"#, e.log().to_vec(), vec!["1. cut 0 bytes".to_string()]);
}

#[test]
fn macros_see_earlier_macros() {
    let mut e = Editor::new("a");
    e.macros = vec![Macro::Append("a".to_string()), Macro::Replace("aa".to_string(), "b".to_string())];
    e.run_macros();
    check!(r#"text "a"; [Append "a", Replace "aa" with "b"]"#, e.text.as_str(), "b");
}

#[test]
fn macros_kept_in_order() {
    let mut e = Editor::new("x");
    e.macros = vec![Macro::Upper, Macro::Append("Y".to_string())];
    e.run_macros();
    e.macros.push(Macro::Append("!".to_string()));
    e.text = "X".to_string();
    e.run_macros();
    e.text.push('Z');
    check!(r#"run once, then add a macro and run"#, e.text.as_str(), "XY!Z");
}

#[test]
fn unicode_cut() {
    let mut e = Editor::new("日本");
    e.cut();
    check!(r#"text "日本"; cut"#, e.log().to_vec(), vec!["1. cut 6 bytes".to_string()]);
}

#[test]
fn paste_after_cut_restores() {
    let mut e = Editor::new("abc");
    e.cut();
    e.paste();
    check!(r#"text "abc"; cut; paste"#, (e.text.as_str(), e.clipboard.as_str()), ("abc", "abc"));
}

#[test]
fn log_numbering_continues() {
    let mut e = Editor::new("q");
    e.cut();
    e.paste();
    e.macros = vec![Macro::Upper];
    e.run_macros();
    check!(r#"cut, paste, run [Upper]"#, e.log().to_vec(), ["1. cut 1 bytes", "2. paste q", "3. upper"].map(String::from).to_vec());
}

#[test]
fn macro_pointer_stable() {
    let mut e = Editor::new("q");
    e.macros = vec![Macro::Upper, Macro::Upper];
    let p = e.macros.as_ptr();
    e.run_macros();
    check!(r#"the macros Vec is the same allocation after run_macros"#, p == e.macros.as_ptr(), true);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6224);
    for _ in 0..300 {
        let len = rng_len(&mut rng);
        let start = rng.string(len, "ab");
        let mut e = Editor::new(&start);
        let (mut text, mut clip, mut log) = (start.clone(), String::new(), Vec::<String>::new());
        let mut ops = Vec::new();
        for _ in 0..5 {
            match rng.below(3) {
                0 => {
                    e.cut();
                    clip = std::mem::take(&mut text);
                    log.push(format!("{}. cut {} bytes", log.len() + 1, clip.len()));
                    ops.push("cut");
                }
                1 => {
                    e.paste();
                    text.push_str(&clip);
                    log.push(format!("{}. paste {clip}", log.len() + 1));
                    ops.push("paste");
                }
                _ => {
                    e.macros = vec![Macro::Replace("a".to_string(), "b".to_string()), Macro::Append("a".to_string())];
                    e.run_macros();
                    text = text.replace('a', "b") + "a";
                    log.push(format!("{}. replace a with b", log.len() + 1));
                    log.push(format!("{}. append a", log.len() + 1));
                    ops.push("run [Replace a b, Append a]");
                }
            }
        }
        check!(format!("text {start:?}; {}", ops.join(", ")), (e.text.clone(), e.clipboard.clone(), e.log().to_vec()), (text, clip, log));
    }
}

fn rng_len(rng: &mut anneal_prelude::Rng) -> usize {
    rng.below(4)
}
