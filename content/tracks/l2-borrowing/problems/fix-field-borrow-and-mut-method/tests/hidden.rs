use solution::*;

#[test]
fn three_appends() {
    check!(r#"append "a", "b", "c""#, { let mut e = Editor { text: String::new(), history: vec![] }; e.append("a"); e.append("b"); e.append("c"); (e.text, e.history) }, ("abc".to_string(), vec![String::new(), "a".to_string(), "ab".to_string()]));
}

#[test]
fn snapshot_is_before() {
    check!(r#"text "x", append "y""#, { let mut e = Editor { text: "x".into(), history: vec![] }; e.append("y"); e.history }, vec!["x".to_string()]);
}

#[test]
fn empty_both() {
    check!(r#"text "", append """#, { let mut e = Editor { text: String::new(), history: vec![] }; e.append(""); (e.text, e.history) }, (String::new(), vec![String::new()]));
}

#[test]
fn long() {
    check!(r#"text 1000 × "a""#, { let mut e = Editor { text: "a".repeat(1000), history: vec![] }; e.append("b"); (e.history[0].len(), e.text.len()) }, (1000, 1001));
}

#[test]
fn newline() {
    check!(r#"text "a\n", append "b""#, { let mut e = Editor { text: "a\n".into(), history: vec![] }; e.append("b"); (e.text, e.history) }, ("a\nb".to_string(), vec!["a\n".to_string()]));
}

#[test]
fn many_appends() {
    check!(r#"100 appends of "x""#, { let mut e = Editor { text: String::new(), history: vec![] }; for _ in 0..100 { e.append("x"); } (e.history.len(), e.history[99].len(), e.text.len()) }, (100, 99, 100));
}

#[test]
fn same_text_twice() {
    check!(r#"text "q", append "" twice"#, { let mut e = Editor { text: "q".into(), history: vec![] }; e.append(""); e.append(""); e.history }, vec!["q".to_string(), "q".to_string()]);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2022);
    for _ in 0..300 {
        let n = rng.below(6);
        let parts: Vec<String> = (0..n).map(|_| { let l = rng.below(3); rng.string(l, "ab") }).collect();
        let mut e = Editor { text: String::new(), history: vec![] };
        let (mut text, mut history) = (String::new(), Vec::new());
        for p in &parts {
            e.append(p);
            history.push(text.clone());
            text.push_str(p);
        }
        check!(format!("appends {parts:?}"), (e.text, e.history), (text, history));
    }
}
