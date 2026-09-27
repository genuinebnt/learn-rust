use solution::*;

#[test]
fn longest_empty_strings() {
    check!(r#"longest("", "")"#, longest("", ""), "");
}

#[test]
fn longest_by_bytes() {
    check!(r#"longest("ééé", "abcd")"#, longest("ééé", "abcd"), "ééé");
}

#[test]
fn longest_of_first_tie() {
    check!(r#"longest_of(["xy", "ab", "z"])"#, longest_of(&["xy", "ab", "z"]), Some("xy"));
}

#[test]
fn longest_of_single() {
    check!(r#"longest_of([""])"#, longest_of(&[""]), Some(""));
}

#[test]
fn keep_longest_tie_keeps() {
    check!(r#"best "ab"; keep_longest("cd")"#, { let mut best = "ab"; (keep_longest(&mut best, "cd"), best) }, (false, "ab"));
}

#[test]
fn keep_longest_from_static() {
    check!(r#"best starts as a literal, then a line from a String"#, { let s = String::from("longer"); let mut best = "x"; keep_longest(&mut best, &s); best.to_string() }, "longer".to_string());
}

#[test]
fn longest_mixed_lifetimes() {
    check!(r#"longest(literal, String) used while the String lives"#, { let s = String::from("dynamic"); longest("st", &s).len() }, 7);
}

#[test]
fn result_is_an_input() {
    let (a, b) = (String::from("x"), String::from("yy"));
    check!(r#"longest returns one of its inputs, not a copy"#, longest(&a, &b).as_ptr() == b.as_ptr(), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6303);
    for _ in 0..300 {
        let n = rng.below(6);
        let mut owned = Vec::new();
        for _ in 0..n {
            let len = rng.below(5);
            owned.push(rng.string(len, "ab"));
        }
        let words: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
        let mut want: Option<&str> = None;
        for &w in &words {
            if want.map_or(true, |b| w.len() > b.len()) {
                want = Some(w);
            }
        }
        check!(format!("longest_of({words:?})"), longest_of(&words), want);
        let mut best = "";
        for &w in &words {
            keep_longest(&mut best, w);
        }
        check!(format!("keep_longest over {words:?}"), best, want.unwrap_or(""));
        if n >= 2 {
            let expect = if words[1].len() > words[0].len() { words[1] } else { words[0] };
            check!(format!("longest({:?}, {:?})", words[0], words[1]), longest(words[0], words[1]), expect);
        }
    }
}
