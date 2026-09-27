pub fn candy(ratings: &[i32]) -> u64 {
    let n = ratings.len();
    let mut give = vec![1u64; n];
    // More than a lower-rated left neighbour...
    for i in 1..n {
        if ratings[i] > ratings[i - 1] {
            give[i] = give[i - 1] + 1;
        }
    }
    // ...and more than a lower-rated right neighbour, keeping the first rule.
    for i in (0..n.saturating_sub(1)).rev() {
        if ratings[i] > ratings[i + 1] {
            give[i] = give[i].max(give[i + 1] + 1);
        }
    }
    give.iter().sum()
}
