pub fn add_head_to_rest(v: &mut [i32]) {
    if v.is_empty() {
        return;
    }
    let head = v[0];
    for x in v.iter_mut() {
        *x += head;
    }
}
