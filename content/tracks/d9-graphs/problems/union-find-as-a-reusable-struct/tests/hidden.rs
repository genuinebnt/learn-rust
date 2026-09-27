use solution::*;

#[test]
fn million_chain() {
    let mut uf = UnionFind::new(1_000_000);
    for i in 0..999_999 {
        uf.union(i, i + 1);
    }
    check!(r#"n = 10⁶; union(i, i + 1) for all i"#, (uf.set_count(), uf.connected(0, 999_999), uf.set_size(500_000)), (1, true, 1_000_000));
}

#[test]
fn self_union() {
    let mut uf = UnionFind::new(4);
    check!(r#"union(2, 2)"#, (uf.union(2, 2), uf.set_count()), (false, 4));
}

#[test]
fn repeated_union() {
    let mut uf = UnionFind::new(3);
    let (a, b, c) = (uf.union(0, 1), uf.union(0, 1), uf.union(1, 0));
    check!(r#"n = 3; union(0,1) twice, then union(1,0)"#, (a, b, c, uf.set_count(), uf.set_size(1)), (true, false, false, 2, 2));
}

#[test]
fn same_root_for_the_whole_set() {
    let mut uf = UnionFind::new(6);
    for (a, b) in [(0, 1), (2, 3), (4, 5), (1, 2), (3, 4)] {
        uf.union(a, b);
    }
    let r = uf.find(0);
    check!(r#"n = 6; union(0,1), union(2,3), union(4,5), union(1,2), union(3,4)"#, (1..6).all(|i| uf.find(i) == r), true);
}

#[test]
fn small_into_big_keeps_sizes() {
    let mut uf = UnionFind::new(6);
    uf.union(0, 1);
    uf.union(2, 3);
    uf.union(0, 2);
    uf.union(5, 0);
    check!(r#"n = 6; build {0,1,2,3}, then union(5, 0)"#, (uf.set_size(5), uf.set_size(3), uf.set_size(4), uf.set_count()), (5, 5, 1, 2));
}

#[test]
fn empty() {
    let uf = UnionFind::new(0);
    check!(r#"n = 0"#, uf.set_count(), 0);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(925);
    for _ in 0..200 {
        let n = 1 + rng.below(8);
        let mut uf = UnionFind::new(n);
        let mut label: Vec<usize> = (0..n).collect();
        let mut log = Vec::new();
        for _ in 0..12 {
            let (a, b) = (rng.below(n), rng.below(n));
            log.push((a, b));
            let (la, lb) = (label[a], label[b]);
            let merged = la != lb;
            for l in label.iter_mut() {
                if *l == lb {
                    *l = la;
                }
            }
            let x = rng.below(n);
            let sets = {
                let mut ls = label.clone();
                ls.sort_unstable();
                ls.dedup();
                ls.len()
            };
            let got = (uf.union(a, b), uf.connected(a, x), uf.set_size(x), uf.set_count());
            let want = (merged, label[a] == label[x], label.iter().filter(|&&l| l == label[x]).count(), sets);
            check!(format!("n = {n}, unions so far = {log:?}; then union({a}, {b}), connected({a}, {x}), set_size({x}), set_count()"), got, want);
        }
    }
}

#[test]
fn scale_union_onto_a_growing_root() {
    // union(0, i) for every i: without size or compression, the path from 0 grows by one each time.
    let n = 200_000;
    let mut uf = UnionFind::new(n);
    for i in 1..n {
        uf.union(0, i);
    }
    check!("n = 200000; union(0, i) for every i", (uf.set_count(), uf.set_size(0), uf.connected(0, n - 1)), (1, n, true));
}
