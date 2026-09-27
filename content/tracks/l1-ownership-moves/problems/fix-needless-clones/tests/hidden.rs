use solution::*;

#[test]
fn longest_tie_last() {
    let lib = Library::new(vec!["ab".into(), "cd".into()]);
    check!(r#"books = ["ab", "cd"]"#, lib.longest(), Some("cd"));
}

#[test]
fn count() {
    check!(r#"needle = "e""#, Library::new(vec!["Dune".into(), "Emma".into(), "Tess".into()]).count_with("e"), 2);
}

#[test]
fn empty() {
    let lib = Library::new(vec![]);
    check!(r#"no books"#, lib.longest(), None);
}

#[test]
fn search_empty_library() {
    let lib = Library::new(vec![]);
    check!(r#"no books, needle = "a""#, lib.search("a"), Vec::<&str>::new());
}

#[test]
fn search_none_match() {
    let lib = Library::new(vec!["Dune".into(), "Emma".into()]);
    check!(r#"books = ["Dune", "Emma"], needle = "x""#, lib.search("x"), Vec::<&str>::new());
}

#[test]
fn search_empty_needle() {
    let lib = Library::new(vec!["b".into(), "a".into()]);
    check!(r#"books = ["b", "a"], needle = """#, lib.search(""), vec!["b", "a"]);
}

#[test]
fn search_middle_of_title() {
    let lib = Library::new(vec!["The Hobbit".into(), "Hob".into()]);
    check!(r#"books = ["The Hobbit", "Hob"], needle = "obb""#, lib.search("obb"), vec!["The Hobbit"]);
}

#[test]
fn case_sensitive() {
    let lib = Library::new(vec!["dune".into(), "Dune".into()]);
    check!(r#"books = ["dune", "Dune"], needle = "D""#, (lib.search("D"), lib.count_with("D")), (vec!["Dune"], 1));
}

#[test]
fn unicode() {
    let lib = Library::new(vec!["Café".into(), "Cafe".into(), "日本".into()]);
    check!(r#"books = ["Café", "Cafe", "日本"], needle = "é" (日本 is 6 bytes, Café 5)"#, (lib.search("é"), lib.longest()), (vec!["Café"], Some("日本")));
}

#[test]
fn longest_tie_of_three_last() {
    let lib = Library::new(vec!["xy".into(), "a".into(), "zw".into(), "uv".into()]);
    check!(r#"books = ["xy", "a", "zw", "uv"]"#, lib.longest(), Some("uv"));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1108);
    for _ in 0..300 {
        let n = rng.below(7);
        let mut books = Vec::new();
        for _ in 0..n {
            let len = rng.below(5);
            books.push(rng.string(len, "abc"));
        }
        let len = rng.below(3);
        let needle = rng.string(len, "abc");
        let lib = Library::new(books.clone());
        let want_search: Vec<&str> = books.iter().filter(|b| b.contains(needle.as_str())).map(|b| b.as_str()).collect();
        let mut want_longest: Option<&str> = None;
        for b in &books {
            if want_longest.map_or(true, |l| b.len() >= l.len()) {
                want_longest = Some(b);
            }
        }
        check!(
            format!("books = {books:?}, needle = {needle:?}"),
            (lib.search(&needle), lib.longest(), lib.count_with(&needle)),
            (want_search.clone(), want_longest, want_search.len())
        );
    }
}
