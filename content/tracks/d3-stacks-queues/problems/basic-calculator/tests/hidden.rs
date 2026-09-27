use solution::*;

#[test]
fn nested_unary() {
    check!(r#""- (3 + (4 + 5))""#, calculate("- (3 + (4 + 5))"), -12);
}

#[test]
fn zero() {
    check!(r#""0""#, calculate("0"), 0);
}

#[test]
fn i32_max() {
    check!(r#""2147483647""#, calculate("2147483647"), 2_147_483_647);
}

#[test]
fn beyond_i32() {
    check!(r#""2147483647 + 2147483647""#, calculate("2147483647 + 2147483647"), 4_294_967_294);
}

#[test]
fn leading_minus() {
    check!(r#""- 1""#, calculate("- 1"), -1);
}

#[test]
fn minus_distributes() {
    check!(r#""1-(2-3)""#, calculate("1-(2-3)"), 2);
}

#[test]
fn redundant_parens() {
    check!(r#""(((7)))""#, calculate("(((7)))"), 7);
}

#[test]
fn multi_digit() {
    check!(r#""12 - 3""#, calculate("12 - 3"), 9);
}

#[test]
fn chain() {
    check!(r#""10 - (2 + 3) - 4""#, calculate("10 - (2 + 3) - 4"), 1);
}

#[test]
fn random_vs_tree() {
    // A random expression tree, printed with + - unary minus and parentheses, and its value.
    fn gen(rng: &mut anneal_prelude::Rng, depth: u32) -> (String, i64) {
        let pick = if depth == 0 { 0 } else { rng.below(5) };
        match pick {
            0 => {
                let n = rng.int(0, 99);
                (n.to_string(), n)
            }
            1 | 2 => {
                let (a, x) = gen(rng, depth - 1);
                let (b, y) = gen(rng, depth - 1);
                if pick == 1 { (format!("{a} + ({b})"), x + y) } else { (format!("{a}-({b})"), x - y) }
            }
            3 => {
                let (a, x) = gen(rng, depth - 1);
                (format!("-({a})"), -x)
            }
            _ => {
                let (a, x) = gen(rng, depth - 1);
                (format!("( {a} )"), x)
            }
        }
    }
    let mut rng = anneal_prelude::Rng::new(3012);
    for _ in 0..300 {
        let (s, want) = gen(&mut rng, 4);
        check!(format!("s = {s:?}"), calculate(&s), want);
    }
}

#[test]
fn scale_100k_nested() {
    let s = format!("{}1{}", "(".repeat(100_000), ")".repeat(100_000));
    check!("100000 nested parentheses around 1", calculate(&s), 1);
}

#[test]
fn scale_100k_terms() {
    let s = "10-9+".repeat(100_000) + "0";
    check!("\"10-9+\" × 100000, then 0", calculate(&s), 100_000);
}

#[test]
fn deep() {
    let s = format!("{}1{}", "(".repeat(5000), ")".repeat(5000));
    check!(r#"5000 nested parentheses around 1"#, calculate(&s), 1);
}
