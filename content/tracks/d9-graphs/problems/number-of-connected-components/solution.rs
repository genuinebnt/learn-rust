pub fn count_components(n: usize, edges: &[(usize, usize)]) -> usize {
    fn root(parent: &mut [usize], mut x: usize) -> usize {
        while parent[x] != x {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        x
    }

    let mut parent: Vec<usize> = (0..n).collect();
    let mut components = n;
    for &(a, b) in edges {
        let (ra, rb) = (root(&mut parent, a), root(&mut parent, b));
        if ra != rb {
            parent[ra] = rb;
            components -= 1;
        }
    }
    components
}
