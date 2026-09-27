pub fn cal_points(ops: &[&str]) -> Option<i64> {
    let mut scores: Vec<i64> = Vec::new();
    for &op in ops {
        match op {
            "+" => {
                let [a, b, ..] = scores[..] else { return None };
                scores.push(a + b);
            }
            "D" => {
                let last = *scores.last()?;
                scores.push(last * 2);
            }
            "C" => {
                scores.pop()?;
            }
            _ => scores.push(op.parse().ok()?),
        }
    }
    Some(scores.iter().map(|&x| i64::from(x)).sum())
}
