use solution::*;

#[test]
fn nums1_empty() {
    check!(r#"nums1 = [0], m = 0, nums2 = [1]"#, { let mut a = [0]; merge(&mut a, 0, &[1]); a }, [1]);
}

#[test]
fn all_smaller() {
    check!(r#"nums1 = [4, 5, 0, 0], m = 2, nums2 = [1, 2]"#, { let mut a = [4, 5, 0, 0]; merge(&mut a, 2, &[1, 2]); a }, [1, 2, 4, 5]);
}
