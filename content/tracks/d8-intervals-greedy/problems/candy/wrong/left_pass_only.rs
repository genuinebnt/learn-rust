pub fn candy(ratings: &[i32]) -> u64 {
    let n = ratings.len();
    let mut give = vec![1u64; n];
    for i in 1..n {
        if ratings[i] > ratings[i - 1] {
            give[i] = give[i - 1] + 1;
        }
    }
    give.iter().sum()
}
