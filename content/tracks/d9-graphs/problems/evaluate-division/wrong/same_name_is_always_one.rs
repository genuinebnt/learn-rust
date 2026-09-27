use std::collections::HashMap;

pub fn calc_equation(equations: &[(&str, &str)], values: &[f64], queries: &[(&str, &str)]) -> Vec<Option<f64>> {
    let mut adj: HashMap<&str, Vec<(&str, f64)>> = HashMap::new();
    for (&(a, b), &v) in equations.iter().zip(values) {
        adj.entry(a).or_default().push((b, v));
        adj.entry(b).or_default().push((a, 1.0 / v));
    }
    queries
        .iter()
        .map(|&(c, d)| {
            if c == d {
                return Some(1.0);
            }
            let mut seen: HashMap<&str, f64> = HashMap::from([(c, 1.0)]);
            let mut stack = vec![c];
            while let Some(u) = stack.pop() {
                if u == d {
                    return Some(seen[u]);
                }
                let here = seen[u];
                for &(v, w) in adj.get(u).map(Vec::as_slice).unwrap_or(&[]) {
                    if !seen.contains_key(v) {
                        seen.insert(v, here * w);
                        stack.push(v);
                    }
                }
            }
            None
        })
        .collect()
}
