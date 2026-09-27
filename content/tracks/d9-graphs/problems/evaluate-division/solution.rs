use std::collections::HashMap;

/// Root of `x` and the ratio `x / root`; every node on the way ends up pointing at the root.
fn find(parent: &mut [usize], ratio: &mut [f64], x: usize) -> (usize, f64) {
    let mut path = Vec::new();
    let mut root = x;
    while parent[root] != root {
        path.push(root);
        root = parent[root];
    }
    // From the node nearest the root outwards, so each parent's ratio is already `parent / root`.
    for &v in path.iter().rev() {
        let p = parent[v];
        if p != root {
            ratio[v] *= ratio[p];
        }
        parent[v] = root;
    }
    (root, if x == root { 1.0 } else { ratio[x] })
}

pub fn calc_equation(equations: &[(&str, &str)], values: &[f64], queries: &[(&str, &str)]) -> Vec<Option<f64>> {
    let mut id: HashMap<&str, usize> = HashMap::new();
    let (mut parent, mut ratio): (Vec<usize>, Vec<f64>) = (Vec::new(), Vec::new());
    for (&(a, b), &v) in equations.iter().zip(values) {
        let mut intern = |name| {
            *id.entry(name).or_insert_with(|| {
                parent.push(parent.len());
                ratio.push(1.0);
                parent.len() - 1
            })
        };
        let (ia, ib) = (intern(a), intern(b));
        let (ra, wa) = find(&mut parent, &mut ratio, ia);
        let (rb, wb) = find(&mut parent, &mut ratio, ib);
        if ra != rb {
            // ra / rb = (a / wa) / (b / wb) = v * wb / wa.
            parent[ra] = rb;
            ratio[ra] = v * wb / wa;
        }
    }
    queries
        .iter()
        .map(|&(c, d)| {
            let (&ic, &id_) = (id.get(c)?, id.get(d)?);
            let (rc, wc) = find(&mut parent, &mut ratio, ic);
            let (rd, wd) = find(&mut parent, &mut ratio, id_);
            (rc == rd).then(|| wc / wd)
        })
        .collect()
}
