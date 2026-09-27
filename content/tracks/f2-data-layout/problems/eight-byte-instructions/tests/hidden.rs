use solution::*;

/// The reference interpreter, straight over the ops.
fn model(ops: &[Op], fuel: u64) -> Option<i64> {
    let mut regs = [0i64; 256];
    let mut pc = 0usize;
    for _ in 0..fuel {
        let op = ops.get(pc)?;
        pc += 1;
        let r = |x: &u8| regs[*x as usize];
        match op {
            Op::Const { dst, value } => regs[*dst as usize] = *value,
            Op::Add { dst, a, b } => regs[*dst as usize] = r(a).wrapping_add(r(b)),
            Op::Sub { dst, a, b } => regs[*dst as usize] = r(a).wrapping_sub(r(b)),
            Op::Mul { dst, a, b } => regs[*dst as usize] = r(a).wrapping_mul(r(b)),
            Op::Lt { dst, a, b } => regs[*dst as usize] = (r(a) < r(b)) as i64,
            Op::Jump { target } => pc = *target as usize,
            Op::BrIf { cond, target } => {
                if r(cond) != 0 {
                    pc = *target as usize;
                }
            }
            Op::BrTable { index, targets, default } => {
                let i = r(index);
                pc = if i >= 0 && (i as u64) < targets.len() as u64 { targets[i as usize] } else { *default } as usize;
            }
            Op::Ret { src } => return Some(r(src)),
        }
    }
    None
}

fn program(ops: &[Op]) -> Program {
    let mut p = Program::new();
    for op in ops {
        p.push(op.clone());
    }
    p
}

/// sum = 0; i = 0; while i < n { sum += i * i; i += 1 }; return sum
fn sum_of_squares(n: i64) -> Vec<Op> {
    vec![
        Op::Const { dst: 0, value: 0 },         // 0: sum
        Op::Const { dst: 1, value: 0 },         // 1: i
        Op::Const { dst: 2, value: n },         // 2: n
        Op::Const { dst: 3, value: 1 },         // 3: one
        Op::Lt { dst: 4, a: 1, b: 2 },          // 4: i < n
        Op::BrIf { cond: 4, target: 7 },        // 5
        Op::Ret { src: 0 },                     // 6
        Op::Mul { dst: 5, a: 1, b: 1 },         // 7
        Op::Add { dst: 0, a: 0, b: 5 },         // 8
        Op::Add { dst: 1, a: 1, b: 3 },         // 9
        Op::Jump { target: 4 },                 // 10
    ]
}

#[test]
fn default_on_negative_and_large() {
    let p = |i: i64| program(&[
        Op::Const { dst: 0, value: i },
        Op::BrTable { index: 0, targets: vec![2, 4], default: 6 },
        Op::Const { dst: 1, value: 10 },
        Op::Ret { src: 1 },
        Op::Const { dst: 1, value: 20 },
        Op::Ret { src: 1 },
        Op::Const { dst: 1, value: 30 },
        Op::Ret { src: 1 },
    ]);
    check!(r#"br_table with index -1 and with 2³² + 1, 2 targets"#, (p(-1).run(10), p(4_294_967_297).run(10), p(1).run(10)), (Some(30), Some(30), Some(20)));
}

#[test]
fn empty_table() {
    check!(r#"br_table with no targets goes to default"#, program(&[Op::BrTable { index: 0, targets: vec![], default: 2 }, Op::Ret { src: 5 }, Op::Const { dst: 0, value: 4 }, Op::Ret { src: 0 }]).run(10), Some(4));
}

#[test]
fn extreme_constants() {
    let p = program(&[
        Op::Const { dst: 0, value: i64::MAX },
        Op::Const { dst: 1, value: i64::MIN },
        Op::Const { dst: 2, value: 1 },
        Op::Add { dst: 3, a: 0, b: 2 },
        Op::Sub { dst: 4, a: 1, b: 2 },
        Op::Add { dst: 5, a: 3, b: 4 },
        Op::Sub { dst: 6, a: 5, b: 5 },
        Op::Ret { src: 6 },
    ]);
    check!(r#"i64::MIN, i64::MAX: MAX + 1 wraps, MIN - 1 wraps"#, p.run(10), Some(0));
}

#[test]
fn fuel_is_exact() {
    let p = program(&[Op::Const { dst: 0, value: 5 }, Op::Ret { src: 0 }]);
    check!(r#"Const, Ret: fuel 1 runs out, fuel 2 returns"#, (p.run(1), p.run(2), p.run(0)), (None, Some(5), None));
}

#[test]
fn push_returns_index() {
    let mut p = Program::new();
    let a = p.push(Op::Const { dst: 0, value: 1 });
    let b = p.push(Op::BrTable { index: 0, targets: vec![0; 100], default: 0 });
    let c = p.push(Op::Ret { src: 0 });
    check!(r#"push three ops"#, (a, b, c, p.len(), p.is_empty()), (0, 1, 2, 3, false));
}

#[test]
fn empty_program() {
    check!(r#"Program::new().run(10)"#, (Program::new().run(10), Program::new().is_empty()), (None, true));
}

#[test]
fn high_registers() {
    check!(r#"registers 200 and 255"#, program(&[Op::Const { dst: 255, value: 9 }, Op::Const { dst: 200, value: 4 }, Op::Lt { dst: 7, a: 200, b: 255 }, Op::Ret { src: 7 }]).run(10), Some(1));
}

#[test]
fn vec_of_a_million() {
    check!(r#"bytes a Vec<Inst> of 1_000_000 takes"#, std::mem::size_of::<Inst>() * 1_000_000, 8_000_000);
}

#[test]
fn loop_to_1000() {
    check!(r#"sum of i * i for i in 0..1000"#, program(&sum_of_squares(1000)).run(100_000), Some(332_833_500));
}

#[test]
fn random_programs_vs_model() {
    let mut rng = anneal_prelude::Rng::new(8209);
    let consts = [0i64, 1, -1, 7, 1 << 40, i64::MIN, i64::MAX, 4_294_967_297];
    for _ in 0..300 {
        let n = 1 + rng.below(14);
        let mut ops = Vec::new();
        for _ in 0..n {
            let reg = |rng: &mut anneal_prelude::Rng| rng.below(4) as u8;
            let target = rng.below(n + 1) as u32;
            let op = match rng.below(9) {
                0 | 1 => Op::Const { dst: reg(&mut rng), value: if rng.bool() { *rng.pick(&consts) } else { rng.int(-50, 50) } },
                2 => Op::Add { dst: reg(&mut rng), a: reg(&mut rng), b: reg(&mut rng) },
                3 => Op::Sub { dst: reg(&mut rng), a: reg(&mut rng), b: reg(&mut rng) },
                4 => Op::Mul { dst: reg(&mut rng), a: reg(&mut rng), b: reg(&mut rng) },
                5 => Op::Lt { dst: reg(&mut rng), a: reg(&mut rng), b: reg(&mut rng) },
                6 => Op::BrIf { cond: reg(&mut rng), target },
                7 => {
                    let k = rng.below(4);
                    let targets: Vec<u32> = rng.vec(k, 0, n as i64);
                    Op::BrTable { index: reg(&mut rng), targets, default: target }
                }
                _ => Op::Ret { src: reg(&mut rng) },
            };
            ops.push(op);
        }
        let fuel = rng.below(60) as u64;
        check!(format!("{ops:?}, run({fuel})"), program(&ops).run(fuel), model(&ops, fuel));
    }
}
