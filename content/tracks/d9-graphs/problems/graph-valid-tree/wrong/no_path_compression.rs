pub fn valid_tree(n: usize, edges: &[(usize, usize)]) -> bool {
    fn root(parent: &[usize], mut x: usize) -> usize {
        while parent[x] != x {
            x = parent[x];
        }
        x
    }

    if edges.len() + 1 != n {
        return false;
    }
    let mut parent: Vec<usize> = (0..n).collect();
    for &(a, b) in edges {
        let (ra, rb) = (root(&parent, a), root(&parent, b));
        if ra == rb {
            return false;
        }
        parent[ra] = rb;
    }
    true
}
