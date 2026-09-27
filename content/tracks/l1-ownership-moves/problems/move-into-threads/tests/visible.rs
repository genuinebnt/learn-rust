use solution::*;

#[test]
fn chunks_in_order() {
    check!(r#"sum_chunks([[1, 2], [3], [4, 5, 6]])"#, sum_chunks(vec![vec![1, 2], vec![3], vec![4, 5, 6]]), vec![3, 3, 15]);
}

#[test]
fn no_chunks() {
    check!(r#"sum_chunks([])"#, sum_chunks(vec![]), Vec::<u64>::new());
}

#[test]
fn parts_split() {
    let data: Vec<u64> = (1..=10).collect();
    check!(r#"sum_parts(1..=10, 3): pieces of 4, 3, 3"#, sum_parts(&data, 3), vec![10, 18, 27]);
}

#[test]
fn data_still_usable() {
    let data = vec![1u64, 2, 3];
    check!(r#"sum_parts borrows: data used afterwards"#, { let s = sum_parts(&data, 2); (s, data.len()) }, (vec![3, 3], 3));
}

#[test]
fn more_parts_than_items() {
    check!(r#"sum_parts([5, 6], 4)"#, sum_parts(&[5, 6], 4), vec![5, 6, 0, 0]);
}
