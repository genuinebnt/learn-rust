use solution::*;

#[test]
fn empty() {
    check!(r#"script([])"#, { let mut v: Vec<i32> = Vec::<i32>::new(); let mut log = Vec::new(); script(&mut v, &mut log); (v, log) }, (vec![2, 2, 2, 2], vec![1, 0]));
}

#[test]
fn one() {
    check!(r#"script([7])"#, { let mut v: Vec<i32> = vec![7]; let mut log = Vec::new(); script(&mut v, &mut log); (v, log) }, (vec![1, 1, 10, 10, 10, 1, 1], vec![3, 3]));
}

#[test]
fn three() {
    check!(r#"script([1, 2, 3])"#, { let mut v: Vec<i32> = vec![1, 2, 3]; let mut log = Vec::new(); script(&mut v, &mut log); (v, log) }, (vec![3, 3, 3, 3, 3, 3, 3], vec![4, 0]));
}

#[test]
fn descending() {
    check!(r#"script([9, 5, 1, 0])"#, { let mut v: Vec<i32> = vec![9, 5, 1, 0]; let mut log = Vec::new(); script(&mut v, &mut log); (v, log) }, (vec![5, 15, 15, 15, 5, 15], vec![2, 4]));
}

#[test]
fn negatives() {
    check!(r#"script([-4, 8, -2, 6, 0])"#, { let mut v: Vec<i32> = vec![-4, 8, -2, 6, 0]; let mut log = Vec::new(); script(&mut v, &mut log); (v, log) }, (vec![8, 8, 8, 8], vec![1, 0]));
}
