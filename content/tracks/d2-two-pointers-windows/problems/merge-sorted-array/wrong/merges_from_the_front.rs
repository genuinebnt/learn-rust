pub fn merge(nums1: &mut [i32], m: usize, nums2: &[i32]) {
    let (mut i, mut j) = (0, 0);
    for w in 0..m + nums2.len() {
        if j >= nums2.len() || (i < m && nums1[i] <= nums2[j]) {
            nums1[w] = nums1[i];
            i += 1;
        } else {
            nums1[w] = nums2[j];
            j += 1;
        }
    }
}
