pub fn merge(nums1: &mut [i32], m: usize, nums2: &[i32]) {
    let mut len = m;
    for &x in nums2 {
        let mut pos = 0;
        while pos < len && nums1[pos] <= x {
            pos += 1;
        }
        let mut k = len;
        while k > pos {
            nums1[k] = nums1[k - 1];
            k -= 1;
        }
        nums1[pos] = x;
        len += 1;
    }
}
