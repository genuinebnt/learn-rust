use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn zero() {
    check!(r#"expression = "0""#, diff_ways_to_compute("0"), vec![0]);
}

#[test]
fn ninety_nine() {
    check!(r#"expression = "99""#, diff_ways_to_compute("99"), vec![99]);
}

#[test]
fn three_minuses() {
    check!(r#"expression = "1-2-3-4""#, sorted(diff_ways_to_compute("1-2-3-4")), vec![-8, -2, -2, 0, 6]);
}

#[test]
fn zero_times() {
    check!(r#"expression = "0*5-3""#, sorted(diff_ways_to_compute("0*5-3")), vec![-3, 0]);
}

#[test]
fn negative_results() {
    check!(r#"expression = "1-99*99""#, sorted(diff_ways_to_compute("1-99*99")), vec![-9800, -9702]);
}

#[test]
fn past_i32() {
    check!(r#"expression = "99*99*99*99*99" (99⁵ > i32::MAX)"#, diff_ways_to_compute("99*99*99*99*99"), vec![9_509_900_499; 14]);
}

#[test]
fn all_three_operators() {
    check!(r#"expression = "2*3*4-5*6+7""#, sorted(diff_ways_to_compute("2*3*4-5*6+7")), vec![-366, -366, -198, -198, -149, -149, -142, -114, -114, -106, -78, -78, -78, -78, -78, -50, -41, -41, -29, -29, -29, -29, -29, -29, -22, -22, -22, -13, -13, 1, 1, 6, 6, 91, 91, 98, 121, 121, 182, 182, 247, 247]);
}

#[test]
fn one_operator() {
    check!(r#"expression = "12*34""#, diff_ways_to_compute("12*34"), vec![408]);
}

/// Every value of tokens i..=j, built bottom-up over interval lengths.
fn brute(nums: &[i64], ops: &[char]) -> Vec<i64> {
    let n = nums.len();
    let mut table = vec![vec![Vec::<i64>::new(); n]; n];
    for i in 0..n {
        table[i][i] = vec![nums[i]];
    }
    for len in 2..=n {
        for i in 0..=n - len {
            let j = i + len - 1;
            let mut vals = Vec::new();
            for k in i..j {
                for &a in &table[i][k] {
                    for &b in &table[k + 1][j] {
                        vals.push(match ops[k] { '+' => a + b, '-' => a - b, _ => a * b });
                    }
                }
            }
            table[i][j] = vals;
        }
    }
    let mut all = table[0][n - 1].clone();
    all.sort();
    all
}

#[test]
fn random_vs_interval_table() {
    let mut rng = anneal_prelude::Rng::new(1128);
    for _ in 0..300 {
        let k = rng.below(6);
        let nums: Vec<i64> = rng.vec(k + 1, 0, 99);
        let ops: Vec<char> = (0..k).map(|_| *rng.pick(&['+', '-', '*'])).collect();
        let mut expr = nums[0].to_string();
        for i in 0..k {
            expr.push(ops[i]);
            expr += &nums[i + 1].to_string();
        }
        check!(format!("expression = {expr:?}"), sorted(diff_ways_to_compute(&expr)), brute(&nums, &ops));
    }
}

#[test]
fn scale_eleven_operators() {
    let got = diff_ways_to_compute("1+2*3-4*5+6*7-8*9+1*2-3");
    let (min, max) = (*got.iter().min().unwrap(), *got.iter().max().unwrap());
    check!("expression = \"1+2*3-4*5+6*7-8*9+1*2-3\"", (got.len(), min, max, got.iter().sum::<i64>()), (58_786, -18_789, 20_601, -5_911_158));
}
