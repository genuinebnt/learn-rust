use solution::*;

#[test]
fn no_products() {
    check!(r#"products = [], search_word = "ab""#, suggested_products(&[], "ab"), vec![Vec::<&str>::new(); 2]);
}

#[test]
fn leetcode_tatiana() {
    check!(r#"products = ["havana"], search_word = "tatiana""#, suggested_products(&["havana"], "tatiana"), vec![Vec::<&str>::new(); 7]);
}

#[test]
fn only_three() {
    check!(r#"products = ["dog", "cat", "cow", "car", "cub"], search_word = "c""#, suggested_products(&["dog", "cat", "cow", "car", "cub"], "c"), vec![vec!["car", "cat", "cow"]]);
}

#[test]
fn shorter_word_sorts_first() {
    check!(r#"products = ["abc", "ab", "abd", "a"], search_word = "a""#, suggested_products(&["abc", "ab", "abd", "a"], "a"), vec![vec!["a", "ab", "abc"]]);
}

#[test]
fn miss_then_would_match() {
    check!(r#"products = ["ab", "b"], search_word = "xb""#, suggested_products(&["ab", "b"], "xb"), vec![Vec::<&str>::new(); 2]);
}

#[test]
fn longer_than_product() {
    check!(r#"products = ["code"], search_word = "codes""#, suggested_products(&["code"], "codes"), vec![vec!["code"], vec!["code"], vec!["code"], vec!["code"], vec![]]);
}

#[test]
fn match_is_whole_prefix() {
    check!(r#"products = ["ab", "xb"], search_word = "ab" ("xb" has a 'b' second, but not the prefix "ab")"#, suggested_products(&["ab", "xb"], "ab"), vec![vec!["ab"], vec!["ab"]]);
}

#[test]
fn reverse_sorted_input() {
    check!(r#"products = ["e", "d", "c", "b", "a"] each prefixed with "k", search_word = "k""#, suggested_products(&["ke", "kd", "kc", "kb", "ka"], "k"), vec![vec!["ka", "kb", "kc"]]);
}

        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1009);
            for _ in 0..300 {
                let mut products: Vec<String> = Vec::new();
                for _ in 0..rng.below(8) {
                    let len = 1 + rng.below(4);
                    let p = rng.string(len, "abc");
                    if !products.contains(&p) {
                        products.push(p);
                    }
                }
                let len = rng.below(5);
                let word = rng.string(len, "abc");
                let refs: Vec<&str> = products.iter().map(|s| s.as_str()).collect();
                let want: Vec<Vec<String>> = (1..=word.len())
                    .map(|k| {
                        let mut m: Vec<String> = products.iter().filter(|p| p.starts_with(&word[..k])).cloned().collect();
                        m.sort();
                        m.truncate(3);
                        m
                    })
                    .collect();
                check!(format!("products = {refs:?}, search_word = {word:?}"), suggested_products(&refs, &word), want);
            }
        }

        #[test]
        fn scale_20k_long_products() {
            // Every product starts with 'a' × 1000, so every prefix of the search word matches all 20000 (listed in shuffled order).
            let base = "a".repeat(1000);
            let products: Vec<String> = (0..20_000).map(|i| format!("{base}{}", base10(i * 7919 % 20_000, 5))).collect();
            let refs: Vec<&str> = products.iter().map(|s| s.as_str()).collect();
            let got = suggested_products(&refs, &base);
            let want = vec![format!("{base}aaaaa"), format!("{base}aaaab"), format!("{base}aaaac")];
            check!("20000 products 'a' × 1000 + five letters, search_word = 'a' × 1000", (got.len(), got.iter().all(|row| *row == want)), (1000, true));
        }

fn base10(mut i: usize, len: usize) -> String {
    let mut w = vec![b'a'; len];
    for k in (0..len).rev() {
        w[k] = b'a' + (i % 10) as u8;
        i /= 10;
    }
    String::from_utf8(w).unwrap()
}
