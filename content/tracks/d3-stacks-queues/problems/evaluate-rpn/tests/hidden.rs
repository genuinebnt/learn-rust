use solution::*;

#[test]
fn single() {
    check!(r#"["-7"]"#, eval_rpn(&["-7"]), -7);
}

#[test]
fn divide_by_negative() {
    check!(r#"["7","-2","/"]"#, eval_rpn(&["7", "-2", "/"]), -3);
}

#[test]
fn zero_numerator() {
    check!(r#"["0","3","/"]"#, eval_rpn(&["0", "3", "/"]), 0);
}

#[test]
fn beyond_i32() {
    check!(r#"["100000","100000","*"]"#, eval_rpn(&["100000", "100000", "*"]), 10_000_000_000);
}

#[test]
fn negative_times_negative() {
    check!(r#"["-3","-4","*"]"#, eval_rpn(&["-3", "-4", "*"]), 12);
}

#[test]
fn left_associative() {
    check!(r#"["1","2","-","3","-"]"#, eval_rpn(&["1", "2", "-", "3", "-"]), -4);
}

#[test]
fn negative_numbers() {
    check!(r#"["-11","-11","+"]"#, eval_rpn(&["-11", "-11", "+"]), -22);
}

#[test]
fn single_zero() {
    check!(r#"["0"]"#, eval_rpn(&["0"]), 0);
}

#[test]
fn random_vs_tree() {
    // Builds a random expression tree, writes it in RPN and returns its value.
    fn gen(rng: &mut anneal_prelude::Rng, depth: u32, out: &mut Vec<String>) -> i64 {
        if depth == 0 || rng.below(3) == 0 {
            let x = rng.int(-9, 9);
            out.push(x.to_string());
            return x;
        }
        let a = gen(rng, depth - 1, out);
        let b = gen(rng, depth - 1, out);
        let (op, v) = match rng.below(4) {
            0 => ("+", a + b),
            1 => ("-", a - b),
            2 => ("*", a * b),
            _ if b != 0 => ("/", a / b),
            _ => ("+", a + b),
        };
        out.push(op.to_string());
        v
    }
    let mut rng = anneal_prelude::Rng::new(3005);
    for _ in 0..400 {
        let mut tokens = Vec::new();
        let want = gen(&mut rng, 4, &mut tokens);
        let refs: Vec<&str> = tokens.iter().map(|t| t.as_str()).collect();
        check!(format!("tokens = {refs:?}"), eval_rpn(&refs), want);
    }
}

#[test]
fn scale_numbers_then_operators() {
    let mut tokens = vec!["1"; 100_001];
    tokens.extend(vec!["+"; 100_000]);
    check!("100001 × \"1\", then 100000 × \"+\"", eval_rpn(&tokens), 100_001);
}
