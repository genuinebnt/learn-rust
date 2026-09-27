pub fn merge_sort(nums: &[i32]) -> Vec<i32> {
    let mut out = nums.to_vec();
    for i in 1..out.len() {
        let mut j = i;
        while j > 0 && out[j - 1] > out[j] {
            out.swap(j - 1, j);
            j -= 1;
        }
    }
    out
}
