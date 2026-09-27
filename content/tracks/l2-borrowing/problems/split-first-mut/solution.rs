pub fn add_head_to_rest(v: &mut [i32]) {
    if let Some((head, rest)) = v.split_first_mut() {
        for x in rest {
            *x += *head;
        }
    }
}
