pub fn can_finish(n: usize, prereqs: &[(usize, usize)]) -> bool {
    let mut parent: Vec<usize> = (0..n).collect();
    fn root(parent: &mut [usize], mut x: usize) -> usize {
        while parent[x] != x {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        x
    }
    for &(a, b) in prereqs {
        let (ra, rb) = (root(&mut parent, a), root(&mut parent, b));
        if ra == rb {
            return false;
        }
        parent[ra] = rb;
    }
    true
}
