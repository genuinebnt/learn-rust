use solution::*;

#[test]
fn leetcode_six() {
    check!(r#"people = [(7, 0), (4, 4), (7, 1), (5, 0), (6, 1), (5, 2)]"#, reconstruct_queue(&[(7, 0), (4, 4), (7, 1), (5, 0), (6, 1), (5, 2)]), vec![(5, 0), (7, 0), (5, 2), (6, 1), (4, 4), (7, 1)]);
}

#[test]
fn leetcode_six_more() {
    check!(r#"people = [(6, 0), (5, 0), (4, 0), (3, 2), (2, 2), (1, 4)]"#, reconstruct_queue(&[(6, 0), (5, 0), (4, 0), (3, 2), (2, 2), (1, 4)]), vec![(4, 0), (5, 0), (2, 2), (3, 2), (1, 4), (6, 0)]);
}

#[test]
fn nobody() {
    check!(r#"people = []"#, reconstruct_queue(&[]), Vec::<(u32, usize)>::new());
}

#[test]
fn one_person() {
    check!(r#"people = [(5, 0)]"#, reconstruct_queue(&[(5, 0)]), vec![(5, 0)]);
}

#[test]
fn equal_height_counts() {
    check!(r#"people = [(5, 1), (5, 0)]"#, reconstruct_queue(&[(5, 1), (5, 0)]), vec![(5, 0), (5, 1)]);
}

#[test]
fn all_zero_means_rising() {
    check!(r#"people = [(3, 0), (1, 0), (2, 0)]"#, reconstruct_queue(&[(3, 0), (1, 0), (2, 0)]), vec![(1, 0), (2, 0), (3, 0)]);
}
