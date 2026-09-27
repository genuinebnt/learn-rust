use solution::*;

#[test]
fn sqe_is_48_bytes() {
    check!(r#"size_of::<Sqe>(), align_of::<Sqe>()"#, (std::mem::size_of::<Sqe>(), std::mem::align_of::<Sqe>()), (48, 8));
}

#[test]
fn opcode_comes_first() {
    check!(r#"offset_of!(Sqe, opcode)"#, std::mem::offset_of!(Sqe, opcode), 0);
}

#[test]
fn quiz_reordered_vs_repr_c() {
    check!(r#"LAYOUT[0..2]: Q1 { u8, u32, u8 } and #[repr(C)] Q2 { u8, u32, u8 }"#, (LAYOUT[0], LAYOUT[1]), ((std::mem::size_of::<Q1>(), std::mem::align_of::<Q1>()), (std::mem::size_of::<Q2>(), std::mem::align_of::<Q2>())));
}

#[test]
fn ring_is_fifo() {
    let mut ring = SqRing::new(4);
    for u in 1..=3 {
        ring.push(Sqe::nop(u)).unwrap();
    }
    check!(r#"SqRing::new(4): push nop 1, 2, 3, then pop 3 times"#, (ring.pop(), ring.pop(), ring.pop(), ring.pop()), (Some(Sqe::nop(1)), Some(Sqe::nop(2)), Some(Sqe::nop(3)), None));
}

#[test]
fn full_ring_hands_entry_back() {
    let mut ring = SqRing::new(2);
    ring.push(Sqe::nop(1)).unwrap();
    ring.push(Sqe::nop(2)).unwrap();
    let extra = Sqe::read(3, 0x1000, 512, 0, 9);
    check!(r#"SqRing::new(2): push nop 1, 2, then read(3, 0x1000, 512, 0, 9)"#, (ring.push(extra), ring.len(), ring.is_full()), (Err(Sqe::read(3, 0x1000, 512, 0, 9)), 2, true));
}

#[test]
fn counters_wrap() {
    let mut ring = SqRing::starting_at(4, u32::MAX - 1);
    for u in 0..3 {
        ring.push(Sqe::nop(u)).unwrap();
    }
    check!(r#"SqRing::starting_at(4, u32::MAX - 1): push 3 entries"#, (ring.len(), ring.head(), ring.tail(), ring.pop().map(|s| s.user_data)), (3, u32::MAX - 1, 1, Some(0)));
}
