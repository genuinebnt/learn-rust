use solution::*;

#[test]
fn classic() {
    check!(r#"nums1 = [1, 2, 3, 0, 0, 0], m = 3, nums2 = [2, 5, 6]"#, { let mut a = [1, 2, 3, 0, 0, 0]; merge(&mut a, 3, &[2, 5, 6]); a }, [1, 2, 2, 3, 5, 6]);
}

#[test]
fn nums2_empty() {
    check!(r#"nums1 = [1], m = 1, nums2 = []"#, { let mut a = [1]; merge(&mut a, 1, &[]); a }, [1]);
}
