pub fn quicksort(v: &mut [i32]) {
    if v.len() <= 1 {
        return;
    }
    let last = v.len() - 1;
    let mut store = 0;
    for i in 0..last {
        if v[i] < v[last] {
            v.swap(i, store);
            store += 1;
        }
    }
    v.swap(store, last);
    let (left, right) = v.split_at_mut(store);
    quicksort(left);
    quicksort(&mut right[1..]);
}
