pub fn bump_below_average(scores: &mut [u32]) {
    for i in 0..scores.len() {
        let avg = scores.iter().map(|&s| s as u64).sum::<u64>() / scores.len() as u64;
        if (scores[i] as u64) < avg {
            scores[i] += 10;
        }
    }
}
