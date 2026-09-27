pub fn add_halves(v: &mut [i32]) {
    let mid = v.len() / 2;
    let (first, second) = v.split_at_mut(mid);
    for (a, b) in first.iter().zip(second.iter_mut()) {
        *b += *a;
    }
}
