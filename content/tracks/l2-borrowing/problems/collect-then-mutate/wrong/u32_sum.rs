pub fn bump_below_average(scores: &mut [u32]) {
    if scores.is_empty() {
        return;
    }
    let avg = scores.iter().sum::<u32>() / scores.len() as u32;
    for s in scores.iter_mut().filter(|s| **s < avg) {
        *s += 10;
    }
}
