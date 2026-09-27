use solution::*;

#[test]
fn empty_chunks_inside() {
    check!(r#"sum_chunks([[], [1], []])"#, sum_chunks(vec![vec![], vec![1], vec![]]), vec![0, 1, 0]);
}

#[test]
fn beyond_u32() {
    check!(r#"sum_chunks([[5000000000, 5000000000]])"#, sum_chunks(vec![vec![5_000_000_000, 5_000_000_000]]), vec![10_000_000_000]);
}

#[test]
fn sixty_four_chunks() {
    check!(r#"64 chunks [i]"#, sum_chunks((0..64).map(|i| vec![i]).collect()), (0..64).collect::<Vec<u64>>());
}

#[test]
fn one_part() {
    check!(r#"sum_parts([1, 2, 3], 1)"#, sum_parts(&[1, 2, 3], 1), vec![6]);
}

#[test]
fn even_split() {
    check!(r#"sum_parts([1, 1, 1, 1, 1, 1], 3)"#, sum_parts(&[1; 6], 3), vec![2, 2, 2]);
}

#[test]
fn longer_pieces_first() {
    check!(r#"sum_parts([1, 10, 100, 1000, 10000], 3): pieces of 2, 2, 1"#, sum_parts(&[1, 10, 100, 1000, 10000], 3), vec![11, 1100, 10000]);
}

#[test]
fn empty_data() {
    check!(r#"sum_parts([], 3)"#, sum_parts(&[], 3), vec![0, 0, 0]);
}

#[test]
fn parts_equal_len() {
    check!(r#"sum_parts([7, 8, 9], 3)"#, sum_parts(&[7, 8, 9], 3), vec![7, 8, 9]);
}

#[test]
fn big_data() {
    let data: Vec<u64> = (1..=200_000).collect();
    check!(r#"sum_parts(1..=200000, 8)"#, sum_parts(&data, 8).iter().sum::<u64>(), 20_000_100_000);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6111);
    for _ in 0..100 {
        let n = rng.below(12);
        let data: Vec<u64> = rng.vec(n, 0, 1_000_000_000_000);
        let parts = rng.below(6) + 1;
        let mut want = Vec::new();
        let mut start = 0;
        for i in 0..parts {
            let len = n / parts + if i < n % parts { 1 } else { 0 };
            want.push(data[start..start + len].iter().sum::<u64>());
            start += len;
        }
        check!(format!("sum_parts({data:?}, {parts})"), sum_parts(&data, parts), want);
        let k = rng.below(5);
        let mut chunks = Vec::new();
        for _ in 0..k {
            let len = rng.below(5);
            chunks.push(rng.vec::<u64>(len, 0, 1000));
        }
        let want: Vec<u64> = chunks.iter().map(|c| c.iter().sum()).collect();
        check!(format!("sum_chunks({chunks:?})"), sum_chunks(chunks.clone()), want);
    }
}
