pub fn suggested_products(products: &[&str], search_word: &str) -> Vec<Vec<String>> {
    (1..=search_word.len())
        .map(|k| products.iter().filter(|p| p.starts_with(&search_word[..k])).take(3).map(|p| p.to_string()).collect())
        .collect()
}
