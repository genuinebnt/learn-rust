pub fn bump_below_average(scores: &mut [u32]) {
    if scores.is_empty() {
        return;
    }
    let avg = scores.iter().map(|&s| s as u64).sum::<u64>() / scores.len() as u64;
    for s in scores.iter_mut().filter(|s| (**s as u64) < avg) {
        *s += 10;
    }
}
