use solution::*;

#[test]
fn valid_count() {
    check!(r#"number of true entries in VALID"#, VALID.iter().filter(|&&v| v).count(), 18);
}

#[test]
fn valid_is_a_const() {
    const X: bool = VALID[0x31] && !VALID[0x00] && TcpFlags::RST.union(TcpFlags::ACK).is_valid();
    check!(r#"a const indexed into VALID"#, X, true);
}

#[test]
fn debug_all() {
    check!(r#"format!("{:?}", TcpFlags::all())"#, format!("{:?}", TcpFlags::all()), "TcpFlags(FIN | SYN | RST | PSH | ACK | URG)");
}

#[test]
fn contains_empty() {
    check!(r#"SYN.contains(empty), SYN.intersects(empty), empty().contains(empty)"#, (TcpFlags::SYN.contains(TcpFlags::empty()), TcpFlags::SYN.intersects(TcpFlags::empty()), TcpFlags::empty().contains(TcpFlags::empty())), (true, false, true));
}

#[test]
fn complement_of_all_and_empty() {
    check!(r#"(!all()).bits(), (!empty()) == all()"#, ((!TcpFlags::all()).bits(), !TcpFlags::empty() == TcpFlags::all(), TcpFlags::FIN.complement().bits()), (0, true, 0x3E));
}

#[test]
fn or_assign_and_sub() {
    let mut f = TcpFlags::SYN;
    f |= TcpFlags::ACK;
    f |= TcpFlags::PSH;
    check!(r#"f = SYN; f |= ACK; f |= PSH; then f - PSH"#, (f.bits(), (f - TcpFlags::PSH).bits(), f.is_valid()), (0x1A, 0x12, true));
}

#[test]
fn default_is_empty() {
    check!(r#"TcpFlags::default()"#, (TcpFlags::default().is_empty(), TcpFlags::default().bits()), (true, 0));
}

#[test]
fn layout_in_arrays() {
    check!(r#"size_of::<[TcpFlags; 64]>(), size_of::<Option<TcpFlags>>(), align_of::<SegmentMeta>()"#, (std::mem::size_of::<[TcpFlags; 64]>(), std::mem::size_of::<Option<TcpFlags>>(), std::mem::align_of::<SegmentMeta>()), (64, 2, 4));
}

#[test]
fn from_bits_edges() {
    check!(r#"from_bits(0x3F), from_bits(0x80), from_bits(0)"#, (TcpFlags::from_bits(0x3F), TcpFlags::from_bits(0x80), TcpFlags::from_bits(0)), (Some(TcpFlags::all()), None, Some(TcpFlags::empty())));
}

#[test]
fn match_on_consts() {
    const SYN_ACK: TcpFlags = TcpFlags::SYN.union(TcpFlags::ACK);
    let kind = match TcpFlags::ACK | TcpFlags::SYN {
        TcpFlags::SYN => "syn",
        SYN_ACK => "syn-ack",
        _ => "other",
    };
    check!(r#"classify SYN | ACK with a match on const flag sets"#, kind, "syn-ack");
}

#[test]
fn random_vs_byte_model() {
    let mut rng = anneal_prelude::Rng::new(8203);
    let valid = [0x02u8, 0x22, 0x12, 0x04, 0x14, 0x11, 0x31, 0x10, 0x30];
    for _ in 0..400 {
        let raw = rng.int(0, 255) as u8;
        check!(format!("from_bits({raw:#04x})"), TcpFlags::from_bits(raw).map(|f| f.bits()), if raw < 0x40 { Some(raw) } else { None });
        check!(format!("from_bits_truncate({raw:#04x})"), TcpFlags::from_bits_truncate(raw).bits(), raw & 0x3F);
        let (a, b) = (raw & 0x3F, rng.int(0, 63) as u8);
        let (fa, fb) = (TcpFlags::from_bits(a).unwrap(), TcpFlags::from_bits(b).unwrap());
        check!(format!("{a:#04x} op {b:#04x}: |, &, -, !a"), ((fa | fb).bits(), (fa & fb).bits(), (fa - fb).bits(), (!fa).bits()),
               (a | b, a & b, a & !b, !a & 0x3F));
        check!(format!("{a:#04x} contains / intersects {b:#04x}"), (fa.contains(fb), fa.intersects(fb)), (a & b == b, a & b != 0));
        check!(format!("{a:#04x}.is_valid()"), (fa.is_valid(), VALID[a as usize]), (valid.contains(&(a & !0x08)), valid.contains(&(a & !0x08))));
    }
}
