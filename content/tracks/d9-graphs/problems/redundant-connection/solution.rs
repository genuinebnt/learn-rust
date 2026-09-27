pub fn find_redundant(edges: &[(usize, usize)]) -> Option<(usize, usize)> {
    fn root(parent: &mut [usize], mut x: usize) -> usize {
        while parent[x] != x {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        x
    }

    let mut parent: Vec<usize> = (0..=edges.len()).collect();
    for &(a, b) in edges {
        let (ra, rb) = (root(&mut parent, a), root(&mut parent, b));
        if ra == rb {
            return Some((a, b));
        }
        parent[ra] = rb;
    }
    None
}
