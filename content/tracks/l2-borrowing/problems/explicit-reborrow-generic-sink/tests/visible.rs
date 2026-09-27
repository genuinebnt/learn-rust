use solution::*;

#[test]
fn pipeline_example() {
    check!(r#"sink [], count 0, xs [7, 8]"#, { let (mut v, mut c) = (Vec::new(), Count(0)); let n = pipeline(&mut v, &mut c, &[7, 8]); (n, v, c.0) }, (6, vec![7, 8, 7, 8, 7, 8], 2));
}

#[test]
fn fan_out_example() {
    check!(r#"sinks [Vec [1], Count(5)], xs [2, 3]"#, { let mut s: Vec<Box<dyn Sink>> = vec![Box::new(vec![1]), Box::new(Count(5))]; fan_out(&mut s, &[2, 3]) }, vec![3, 7]);
}

#[test]
fn lend_a_trait_object() {
    check!(r#"emit_all into a &mut dyn Sink, then read the Vec"#, { let mut v = vec![0]; { let d: &mut dyn Sink = &mut v; emit_all(d, &[4]); } v }, vec![0, 4]);
}

#[test]
fn box_is_a_sink() {
    check!(r#"emit_all into a Box<Count>"#, { let mut b = Box::new(Count(0)); emit_all(&mut b, &[1, 2, 3]); b.len() }, 3);
}

#[test]
fn lend_twice() {
    check!(r#"emit_all(&mut v, [1]) twice"#, { let mut v = Vec::new(); emit_all(&mut v, &[1]); emit_all(&mut v, &[1]); v }, vec![1, 1]);
}
