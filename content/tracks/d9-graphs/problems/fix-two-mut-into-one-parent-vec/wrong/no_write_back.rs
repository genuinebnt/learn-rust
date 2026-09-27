/// Root of `x`, pointing every node on the way straight at the root.
pub fn find(parent: &mut [usize], x: usize) -> usize {
    let p = parent[x];
    if p != x {
        return find(parent, p);
    }
    x
}

/// Merges the sets holding `a` and `b`. Returns false if they were already together.
pub fn union(parent: &mut [usize], a: usize, b: usize) -> bool {
    let (ra, rb) = (find(parent, a), find(parent, b));
    if ra == rb {
        return false;
    }
    parent[ra] = rb;
    true
}
