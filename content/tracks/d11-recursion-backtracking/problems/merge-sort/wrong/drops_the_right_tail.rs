pub fn merge_sort(nums: &[i32]) -> Vec<i32> {
    if nums.len() <= 1 {
        return nums.to_vec();
    }
    let (left, right) = nums.split_at(nums.len() / 2);
    let (left, right) = (merge_sort(left), merge_sort(right));
    let mut out = Vec::with_capacity(nums.len());
    let (mut i, mut j) = (0, 0);
    while i < left.len() && j < right.len() {
        if left[i] <= right[j] {
            out.push(left[i]);
            i += 1;
        } else {
            out.push(right[j]);
            j += 1;
        }
    }
    out.extend_from_slice(&left[i..]);
    out
}
