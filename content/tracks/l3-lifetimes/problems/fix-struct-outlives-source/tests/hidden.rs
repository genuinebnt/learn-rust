use solution::*;

#[test]
fn no_docs() {
    check!(r#"[]"#, (excerpts(&[]).len(), biggest(&[])), (0, None));
}

#[test]
fn empty_doc() {
    let docs = [""].map(String::from);
    check!(r#"[""]"#, excerpts(&docs), vec![Excerpt { title: "", first_line: "" }]);
}

#[test]
fn only_blank_after_title() {
    let docs = ["T\n \n	\n"].map(String::from);
    check!(r#"["T\n \n\t\n"]"#, excerpts(&docs), vec![Excerpt { title: "T", first_line: "" }]);
}

#[test]
fn separator_first() {
    check!(r#""---\nA\nB""#, body_excerpt("---\nA\nB"), Excerpt { title: "A", first_line: "B" });
}

#[test]
fn two_separators() {
    check!(r#""x\n---\ny\n---\nz""#, body_excerpt("x\n---\ny\n---\nz"), Excerpt { title: "y", first_line: "---" });
}

#[test]
fn biggest_later_wins() {
    let docs = ["a", "b\nc\nd", "e\nf"].map(String::from);
    check!(r#"["a", "b\nc\nd", "e\nf"]"#, biggest(&docs), Some(Excerpt { title: "b", first_line: "c" }));
}

#[test]
fn biggest_counts_lines_not_bytes() {
    let docs = ["long line here", "a\nb"].map(String::from);
    check!(r#"["long line here", "a\nb"]"#, biggest(&docs), Some(Excerpt { title: "a", first_line: "b" }));
}

#[test]
fn body_points_into_raw() {
    let raw = String::from("---\nZ");
    check!(r#"body_excerpt's title points into raw"#, body_excerpt(&raw).title.as_ptr() == raw[4..].as_ptr(), true);
}

#[test]
fn unicode() {
    let docs = ["日本\r\n 語 "].map(String::from);
    check!(r#"["日本\r\n 語 "]"#, excerpts(&docs), vec![Excerpt { title: "日本", first_line: "語" }]);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6306);
    for _ in 0..300 {
        let n = rng.below(4);
        let mut docs: Vec<String> = Vec::new();
        for _ in 0..n {
            let len = rng.below(10);
            docs.push(rng.string(len, "ab \n\r"));
        }
        let model = |d: &str| {
            let mut lines = d.lines().map(str::trim);
            let t = lines.next().unwrap_or("").to_string();
            let f = lines.find(|l| !l.is_empty()).unwrap_or("").to_string();
            (t, f)
        };
        let got: Vec<(String, String)> = excerpts(&docs).iter().map(|e| (e.title.to_string(), e.first_line.to_string())).collect();
        let want: Vec<(String, String)> = docs.iter().map(|d| model(d)).collect();
        check!(format!("excerpts({docs:?})"), got, want);
        let mut best: Option<&String> = None;
        for d in &docs {
            if best.map_or(true, |b| d.lines().count() > b.lines().count()) {
                best = Some(d);
            }
        }
        let got = biggest(&docs).map(|e| (e.title.to_string(), e.first_line.to_string()));
        check!(format!("biggest({docs:?})"), got, best.map(|b| model(b)));
    }
}
