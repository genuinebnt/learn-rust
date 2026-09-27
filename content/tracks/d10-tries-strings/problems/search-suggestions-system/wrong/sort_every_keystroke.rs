pub fn suggested_products(products: &[&str], search_word: &str) -> Vec<Vec<String>> {
    (1..=search_word.len())
        .map(|k| {
            let mut matches: Vec<&str> = products.iter().copied().filter(|p| p.starts_with(&search_word[..k])).collect();
            matches.sort_unstable();
            matches.iter().take(3).map(|p| p.to_string()).collect()
        })
        .collect()
}
