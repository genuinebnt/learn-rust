use solution::*;

#[test]
fn size_one() {
    check!(r#"size 1"#, { let mut b = Batcher::new(1); (b.push(5), b.flush()) }, (Some(vec![5]), None));
}

#[test]
fn flush_empty() {
    check!(r#"nothing pushed"#, Batcher::new(4).flush(), None);
}

#[test]
fn flush_after_full_batch() {
    check!(r#"size 2, push 1, 2, then flush"#, { let mut b = Batcher::new(2); b.push(1); (b.push(2), b.flush()) }, (Some(vec![1, 2]), None));
}

#[test]
fn push_after_flush() {
    check!(r#"size 3, push 1, flush, push 2, 3, 4"#, { let mut b = Batcher::new(3); b.push(1); let f = b.flush(); (f, b.push(2), b.push(3), b.push(4)) }, (Some(vec![1]), None, None, Some(vec![2, 3, 4])));
}

#[test]
fn size_one_every_push() {
    check!(r#"size 1, push 1, 2, 3"#, { let mut b = Batcher::new(1); (b.push(1), b.push(2), b.push(3)) }, (Some(vec![1]), Some(vec![2]), Some(vec![3])));
}

#[test]
fn extreme_values() {
    check!(r#"size 2, push 0, u32::MAX"#, { let mut b = Batcher::new(2); (b.push(0), b.push(u32::MAX)) }, (None, Some(vec![0, u32::MAX])));
}

#[test]
fn duplicates() {
    check!(r#"size 3, push 7, 7, 7"#, { let mut b = Batcher::new(3); (b.push(7), b.push(7), b.push(7)) }, (None, None, Some(vec![7, 7, 7])));
}

#[test]
fn big_batches() {
    check!(r#"size 1000, push 0..2500, then flush"#, { let mut b = Batcher::new(1000); let full: Vec<Vec<u32>> = (0..2500).filter_map(|i| b.push(i)).collect(); (full.len(), full[1][999], b.flush().map(|r| (r.len(), r[0]))) }, (2, 1999, Some((500, 2000))));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(1116);
    for _ in 0..300 {
        let size = rng.below(5) + 1;
        let mut b = Batcher::new(size);
        let mut pending: Vec<u32> = Vec::new();
        let mut ops = Vec::new();
        for _ in 0..rng.below(15) {
            if rng.below(4) == 0 {
                ops.push("flush".to_string());
                let want = if pending.is_empty() { None } else { Some(std::mem::take(&mut pending)) };
                check!(format!("size = {size}, {ops:?}"), b.flush(), want);
            } else {
                let v = rng.below(100) as u32;
                ops.push(format!("push {v}"));
                pending.push(v);
                let want = if pending.len() == size { Some(std::mem::take(&mut pending)) } else { None };
                check!(format!("size = {size}, {ops:?}"), b.push(v), want);
            }
        }
    }
}
