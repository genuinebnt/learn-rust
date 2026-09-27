pub fn merge(nums1: &mut [i32], m: usize, nums2: &[i32]) {
    let (mut i, mut j, mut w) = (m, nums2.len(), m + nums2.len());
    while j > 0 {
        w -= 1;
        if i > 0 && nums1[i - 1] > nums2[j - 1] {
            nums1[w] = nums1[i - 1];
            i -= 1;
        } else {
            nums1[w] = nums2[j - 1];
            j -= 1;
        }
    }
}
