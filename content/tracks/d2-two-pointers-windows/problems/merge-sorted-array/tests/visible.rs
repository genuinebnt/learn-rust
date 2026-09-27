use solution::*;

#[test]
fn classic() {
    check!(r#"nums1 = [1, 2, 3, 0, 0, 0], m = 3, nums2 = [2, 5, 6]"#, { let mut a = [1, 2, 3, 0, 0, 0]; merge(&mut a, 3, &[2, 5, 6]); a }, [1, 2, 2, 3, 5, 6]);
}

#[test]
fn nums2_empty() {
    check!(r#"nums1 = [1], m = 1, nums2 = []"#, { let mut a = [1]; merge(&mut a, 1, &[]); a }, [1]);
}

#[test]
fn nums2_smaller() {
    check!(r#"nums1 = [4, 5, 0, 0], m = 2, nums2 = [1, 2]"#, { let mut a = [4, 5, 0, 0]; merge(&mut a, 2, &[1, 2]); a }, [1, 2, 4, 5]);
}

#[test]
fn nums1_has_no_values() {
    check!(r#"nums1 = [0], m = 0, nums2 = [1]"#, { let mut a = [0]; merge(&mut a, 0, &[1]); a }, [1]);
}

#[test]
fn equal_values() {
    check!(r#"nums1 = [1, 3, 0, 0], m = 2, nums2 = [1, 3]"#, { let mut a = [1, 3, 0, 0]; merge(&mut a, 2, &[1, 3]); a }, [1, 1, 3, 3]);
}
