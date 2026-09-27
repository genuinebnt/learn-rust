use solution::*;

#[test]
fn pipeline_empty() {
    check!(r#"xs []"#, { let (mut v, mut c) = (vec![9], Count(0)); (pipeline(&mut v, &mut c, &[]), c.0) }, (1, 0));
}

#[test]
fn pipeline_keeps_existing() {
    check!(r#"sink [5], xs [1]"#, { let (mut v, mut c) = (vec![5], Count(1)); let n = pipeline(&mut v, &mut c, &[1]); (n, v, c.0) }, (4, vec![5, 1, 1, 1], 2));
}

#[test]
fn fan_out_empty() {
    check!(r#"no sinks"#, fan_out(&mut [], &[1]), Vec::<usize>::new());
}

#[test]
fn nested_lending() {
    check!(r#"emit_all into &mut &mut Vec"#, { let mut v = Vec::new(); let mut r = &mut v; emit_all(&mut r, &[6]); emit_all(r, &[7]); v }, vec![6, 7]);
}

#[test]
fn box_dyn_by_value() {
    check!(r#"emit_all(Box<dyn Sink> by value) then nothing"#, { let b: Box<dyn Sink> = Box::new(Count(0)); let mut b = b; emit_all(&mut b, &[1]); emit_all(&mut b, &[2]); b.len() }, 2);
}

#[test]
fn tee_of_lent_sinks() {
    check!(r#"Tee(&mut a, &mut b)"#, { let (mut a, mut b) = (Vec::new(), Count(0)); emit_all(Tee(&mut a, &mut b), &[1, 2]); (a, b.0) }, (vec![1, 2], 2));
}

#[test]
fn tee_of_boxed() {
    check!(r#"Tee(Box<dyn Sink>, Count) through &mut"#, { let mut t = Tee(Box::new(vec![0]) as Box<dyn Sink>, Count(0)); emit_all(&mut t, &[3]); (t.0.len(), t.1.len()) }, (2, 1));
}

#[test]
fn fan_out_repeated() {
    check!(r#"fan_out twice into [Count(0)]"#, { let mut s: Vec<Box<dyn Sink>> = vec![Box::new(Count(0))]; fan_out(&mut s, &[1, 1]); fan_out(&mut s, &[1]) }, vec![3]);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6216);
    for _ in 0..300 {
        let n = rng.below(6);
        let xs: Vec<i32> = rng.vec(n, -9, 9);
        let len = rng.below(3);
        let start: Vec<i32> = rng.vec(len, 0, 9);
        let c0 = rng.below(5);
        let mut v = start.clone();
        let mut c = Count(c0);
        let got = pipeline(&mut v, &mut c, &xs);
        let mut want = start.clone();
        for _ in 0..3 {
            want.extend_from_slice(&xs);
        }
        check!(format!("sink {start:?}, count {c0}, xs {xs:?}"), (got, v, c.0), (want.len(), want, c0 + n));
    }
}

#[test]
fn many_values() {
    let xs: Vec<i32> = (0..100_000).collect();
    let mut s: Vec<Box<dyn Sink>> = vec![Box::new(Vec::new()), Box::new(Count(0))];
    check!("fan_out 100000 values into [Vec, Count]", fan_out(&mut s, &xs), vec![100_000, 100_000]);
}
