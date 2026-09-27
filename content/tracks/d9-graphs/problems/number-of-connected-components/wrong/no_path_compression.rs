pub fn count_components(n: usize, edges: &[(usize, usize)]) -> usize {
    fn root(parent: &[usize], mut x: usize) -> usize {
        while parent[x] != x {
            x = parent[x];
        }
        x
    }

    let mut parent: Vec<usize> = (0..n).collect();
    let mut components = n;
    for &(a, b) in edges {
        let (ra, rb) = (root(&parent, a), root(&parent, b));
        if ra != rb {
            parent[ra] = rb;
            components -= 1;
        }
    }
    components
}
