use solution::*;

#[test]
fn hashtags_existing_tag() {
    let mut d = Document { title: "Draft".to_string(), tags: vec![], lines: vec![], words: 0 };
    d.tags.push("rust".to_string());
    d.body().push_line("#rust #go");
    check!(r##"tags [rust]; line "#rust #go""##, (hashtags(&mut d), d.tags.clone()), (1, vec!["rust".to_string(), "go".to_string()]));
}

#[test]
fn hashtags_none() {
    let mut d = Document { title: "Draft".to_string(), tags: vec![], lines: vec![], words: 0 };
    d.body().push_line("no tags here");
    check!(r#"line "no tags here""#, (hashtags(&mut d), d.tags.len()), (0, 0));
}

#[test]
fn hashtags_empty_doc() {
    let mut d = Document { title: "Draft".to_string(), tags: vec![], lines: vec![], words: 0 };
    check!(r#"empty document"#, hashtags(&mut d), 0);
}

#[test]
fn hashtag_mid_word_ignored() {
    let mut d = Document { title: "Draft".to_string(), tags: vec![], lines: vec![], words: 0 };
    d.body().push_line("a#b ##c");
    check!(r#"line "a#b ##c""#, (hashtags(&mut d), d.tags.clone()), (1, vec!["#c".to_string()]));
}

#[test]
fn hashtag_unicode() {
    let mut d = Document { title: "Draft".to_string(), tags: vec![], lines: vec![], words: 0 };
    d.body().push_line("#日本 #é");
    hashtags(&mut d);
    check!(r##"line "#日本 #é""##, d.tags.clone(), ["日本", "é"].map(String::from).to_vec());
}

#[test]
fn retitle_empty() {
    let mut d = Document { title: "Draft".to_string(), tags: vec![], lines: vec![], words: 0 };
    d.header().retitle("");
    check!(r#"retitle """#, (d.title.as_str(), d.tags.len()), ("", 1));
}

#[test]
fn edited_already_there() {
    let mut d = Document { title: "Draft".to_string(), tags: vec![], lines: vec![], words: 0 };
    d.tags.push("edited".to_string());
    d.header().retitle("x");
    check!(r#"tags [edited]; retitle"#, d.tags.clone(), vec!["edited".to_string()]);
}

#[test]
fn words_accumulate() {
    let mut d = Document { title: "Draft".to_string(), tags: vec![], lines: vec![], words: 0 };
    d.words = 5;
    d.body().push_line("x y");
    check!(r#"words 5; push "x y""#, d.words, 7);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6228);
    for _ in 0..300 {
        let mut d = Document { title: String::new(), tags: vec![], lines: vec![], words: 0 };
        let mut lines = Vec::new();
        for _ in 0..rng_len(&mut rng) {
            let len = rng.below(8);
            lines.push(rng.string(len, "#ab "));
        }
        for l in &lines {
            d.body().push_line(l);
        }
        let mut tags: Vec<String> = Vec::new();
        let mut added = 0;
        for l in &lines {
            for w in l.split_whitespace() {
                if let Some(t) = w.strip_prefix('#') {
                    if !t.is_empty() && !tags.iter().any(|x| x == t) {
                        tags.push(t.to_string());
                        added += 1;
                    }
                }
            }
        }
        let words: usize = lines.iter().map(|l| l.split_whitespace().count()).sum();
        let got = hashtags(&mut d);
        check!(format!("lines {lines:?}"), (got, d.tags.clone(), d.words), (added, tags, words));
    }
}

fn rng_len(rng: &mut anneal_prelude::Rng) -> usize {
    rng.below(5)
}
