fn best(strs: &[&str], m: usize, n: usize) -> usize {
    match strs {
        [] => 0,
        [s, rest @ ..] => {
            let zeros = s.bytes().filter(|&b| b == b'0').count();
            let ones = s.len() - zeros;
            let skip = best(rest, m, n);
            if zeros <= m && ones <= n { skip.max(1 + best(rest, m - zeros, n - ones)) } else { skip }
        }
    }
}

pub fn find_max_form(strs: &[&str], m: usize, n: usize) -> usize {
    best(strs, m, n)
}
