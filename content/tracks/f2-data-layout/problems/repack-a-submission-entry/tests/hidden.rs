use solution::*;

#[test]
fn quiz_tuple_is_reordered() {
    check!(r#"LAYOUT[2]: (u8, u64, u8)"#, LAYOUT[2], (std::mem::size_of::<Q3>(), std::mem::align_of::<Q3>()));
}

#[test]
fn quiz_trailing_padding() {
    check!(r#"LAYOUT[3..5]: #[repr(C)] Q4 { u64, u8 } and [Q4; 2]"#, (LAYOUT[3], LAYOUT[4]), ((std::mem::size_of::<Q4>(), std::mem::align_of::<Q4>()), (std::mem::size_of::<Q5>(), std::mem::align_of::<Q5>())));
}

#[test]
fn quiz_nested() {
    check!(r#"LAYOUT[5]: #[repr(C)] Q6 { u8, Q2 }"#, LAYOUT[5], (std::mem::size_of::<Q6>(), std::mem::align_of::<Q6>()));
}

#[test]
fn quiz_arrays() {
    check!(r#"LAYOUT[6..8]: (u8, [u16; 3]) and [u64; 0]"#, (LAYOUT[6], LAYOUT[7]), ((std::mem::size_of::<Q7>(), std::mem::align_of::<Q7>()), (std::mem::size_of::<Q8>(), std::mem::align_of::<Q8>())));
}

#[test]
fn no_holes_anywhere() {
    use std::mem::{offset_of, size_of};
    let mut spans = vec![
        (offset_of!(Sqe, opcode), 1),
        (offset_of!(Sqe, flags), 1),
        (offset_of!(Sqe, ioprio), 2),
        (offset_of!(Sqe, fd), 4),
        (offset_of!(Sqe, off), 8),
        (offset_of!(Sqe, addr), 8),
        (offset_of!(Sqe, len), 4),
        (offset_of!(Sqe, rw_flags), 4),
        (offset_of!(Sqe, user_data), 8),
        (offset_of!(Sqe, buf_index), 2),
        (offset_of!(Sqe, personality), 2),
        (offset_of!(Sqe, file_index), 4),
    ];
    spans.sort();
    // Each field starts where the previous one ended, and the last one ends at size_of.
    let mut end = 0;
    let mut holes = Vec::new();
    for &(at, len) in &spans {
        if at != end {
            holes.push((end, at));
        }
        end = at + len;
    }
    if end != size_of::<Sqe>() {
        holes.push((end, size_of::<Sqe>()));
    }
    check!("padding holes in Sqe as (from, to) byte ranges", holes, Vec::<(usize, usize)>::new());
}

#[test]
fn ring_of_4096_entries() {
    check!(r#"size_of::<[Sqe; 4096]>()"#, std::mem::size_of::<[Sqe; 4096]>(), 196608);
}

#[test]
fn constructors_keep_fields() {
    let s = Sqe::write(7, 0xdead0000, 4096, 1 << 40, 77);
    check!(r#"Sqe::write(7, 0xdead0000, 4096, 1 << 40, 77)"#, (s.opcode, s.fd, s.addr, s.len, s.off, s.user_data, s.flags, s.file_index), (OP_WRITE, 7, 0xdead0000, 4096, 1 << 40, 77, 0, 0));
}

#[test]
fn empty_ring() {
    let mut ring = SqRing::new(1);
    let first_pop = ring.pop();
    check!(r#"SqRing::new(1): pop, then push twice"#, (first_pop, ring.push(Sqe::nop(5)), ring.push(Sqe::nop(6)), ring.is_empty()), (None, Ok(()), Err(Sqe::nop(6)), false));
}

#[test]
fn full_across_the_wrap() {
    let mut ring = SqRing::starting_at(8, u32::MAX - 3);
    for u in 0..8 {
        ring.push(Sqe::nop(u)).unwrap();
    }
    ring.pop();
    ring.push(Sqe::nop(8)).unwrap();
    check!(r#"SqRing::starting_at(8, u32::MAX - 3): push 8, pop 1, push 1"#, (ring.len(), ring.is_full(), ring.head(), ring.tail()), (8, true, u32::MAX - 2, 5));
}

#[test]
#[should_panic]
fn entries_must_be_a_power_of_two() {
    SqRing::new(6);
}

#[test]
fn random_vs_vecdeque() {
    let mut rng = anneal_prelude::Rng::new(8201);
    for _ in 0..300 {
        let entries = 1u32 << rng.below(4);
        let start = if rng.bool() { u32::MAX - rng.below(6) as u32 } else { rng.below(1000) as u32 };
        let mut ring = SqRing::starting_at(entries, start);
        let mut model = std::collections::VecDeque::new();
        let mut log = Vec::new();
        for step in 0..40u64 {
            if rng.below(3) < 2 {
                let sqe = Sqe::nop(step);
                log.push(format!("push {step}"));
                let want = if model.len() == entries as usize { Err(sqe) } else { model.push_back(sqe); Ok(()) };
                check!(format!("entries {entries}, start {start}: {}", log.join(", ")), ring.push(sqe), want);
            } else {
                log.push("pop".to_string());
                check!(format!("entries {entries}, start {start}: {}", log.join(", ")), ring.pop(), model.pop_front());
            }
            check!(format!("entries {entries}, start {start}: {}; len", log.join(", ")), (ring.len(), ring.is_full()), (model.len(), model.len() == entries as usize));
        }
    }
}
