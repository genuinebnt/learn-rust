pub fn candy(ratings: &[i32]) -> u64 {
    let n = ratings.len();
    let mut give = vec![1u64; n];
    let mut changed = true;
    while changed {
        changed = false;
        for i in 0..n {
            if i > 0 && ratings[i] > ratings[i - 1] && give[i] <= give[i - 1] {
                give[i] = give[i - 1] + 1;
                changed = true;
            }
            if i + 1 < n && ratings[i] > ratings[i + 1] && give[i] <= give[i + 1] {
                give[i] = give[i + 1] + 1;
                changed = true;
            }
        }
    }
    give.iter().sum()
}
