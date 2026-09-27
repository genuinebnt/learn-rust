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
fn inst_is_8_bytes() {
    check!(r#"size_of::<Inst>(), size_of::<Option<Inst>>()"#, (std::mem::size_of::<Inst>(), std::mem::size_of::<Option<Inst>>()), (8, 8));
}

#[test]
fn loop_sum_of_squares() {
    check!(r#"sum of i * i for i in 0..10, run(1000)"#, program(&sum_of_squares(10)).run(1000), Some(285));
}

#[test]
fn big_constant() {
    let p = program(&[Op::Const { dst: 0, value: 1 << 40 }, Op::Const { dst: 1, value: -3 }, Op::Mul { dst: 2, a: 0, b: 1 }, Op::Ret { src: 2 }]);
    check!(r#"Const r0 = 1 << 40; Const r1 = -3; Mul r2 = r0 * r1; Ret r2"#, p.run(10), Some(-3 * (1i64 << 40)));
}

#[test]
fn jump_table() {
    let mut ops = vec![Op::Const { dst: 0, value: 2 }, Op::BrTable { index: 0, targets: vec![2, 4, 6], default: 8 }];
    for t in [2, 4, 6, 8] {
        ops.push(Op::Const { dst: 1, value: 10 * t });
        ops.push(Op::Ret { src: 1 });
    }
    let p = program(&ops);
    check!(r#"r0 = 2; br_table r0 [2, 4, 6] default 8; each target t does r1 = 10 * t and returns it"#, p.run(10), Some(60));
}

#[test]
fn runs_out() {
    check!(r#"an infinite loop with fuel 100, and running off the end"#, (program(&[Op::Jump { target: 0 }]).run(100), program(&[Op::Const { dst: 0, value: 1 }]).run(100)), (None, None));
}
