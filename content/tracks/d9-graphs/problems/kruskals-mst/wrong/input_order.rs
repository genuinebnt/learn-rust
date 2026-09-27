pub fn mst_weight(n: usize, edges: &[(usize, usize, u64)]) -> Option<u64> {
    fn root(parent: &mut [usize], mut x: usize) -> usize {
        while parent[x] != x {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        x
    }

    let mut parent: Vec<usize> = (0..n).collect();
    let (mut total, mut used) = (0, 0);
    for &(a, b, w) in edges {
        let (ra, rb) = (root(&mut parent, a), root(&mut parent, b));
        if ra != rb {
            parent[ra] = rb;
            total += w;
            used += 1;
        }
    }
    (used + 1 == n).then_some(total)
}
