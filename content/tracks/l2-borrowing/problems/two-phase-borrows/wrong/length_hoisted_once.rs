/// Runs these steps on `v` in order. "len" always means the length at that step.
///  1. push len
///  2. swap the first and last elements
///  3. insert a copy of the first element at index len / 2
///  4. add len to the last element
///  5. move the last element to the front
///  6. rotate left by len / 3
///  7. remove every element smaller than the first
///  8. log len
///  9. drop the last len / 4 elements
/// 10. pad with two copies of the last element
/// 11. append a copy of the first len / 2 elements
/// 12. log how many elements are greater than the first
pub fn script(v: &mut Vec<i32>, log: &mut Vec<usize>) {
    v.push(v.len() as i32);
    let n = v.len();
    v.swap(0, n - 1);
    v.insert(v.len() / 2, v[0]);
    v[n - 1] += n as i32;
    let last = v.pop().unwrap();
    v.insert(0, last);
    v.rotate_left(n / 3);
    let first = v[0];
    v.retain(|&x| x >= first);
    log.push(v.len());
    v.truncate(v.len() - v.len() / 4);
    v.resize(v.len() + 2, v[v.len() - 1]);
    v.extend_from_within(..v.len() / 2);
    log.push(v.iter().filter(|&&x| x > v[0]).count());
}
