pub fn suggested_products(products: &[&str], search_word: &str) -> Vec<Vec<String>> {
    let mut sorted = products.to_vec();
    sorted.sort_unstable();
    search_word
        .bytes()
        .enumerate()
        .map(|(k, b)| sorted.iter().filter(|p| p.as_bytes().get(k) == Some(&b)).take(3).map(|p| p.to_string()).collect())
        .collect()
}
