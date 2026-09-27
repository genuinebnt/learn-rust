use solution::*;

#[test]
fn one_byte() {
    check!(r#"size_of::<TcpFlags>(), size_of::<SegmentMeta>()"#, (std::mem::size_of::<TcpFlags>(), std::mem::size_of::<SegmentMeta>()), (1, 12));
}

#[test]
fn usable_in_const_items() {
    const SYN_ACK: TcpFlags = TcpFlags::SYN.union(TcpFlags::ACK);
    const BARE_SYN: TcpFlags = SYN_ACK.difference(TcpFlags::ACK);
    const CHECKS: [bool; 3] = [SYN_ACK.contains(TcpFlags::SYN), BARE_SYN.is_valid(), TcpFlags::SYN.union(TcpFlags::FIN).is_valid()];
    check!("SYN_ACK.bits(), BARE_SYN.bits(), [SYN_ACK ⊇ SYN, SYN valid, SYN|FIN valid]", (SYN_ACK.bits(), BARE_SYN.bits(), CHECKS), (0x12, 0x02, [true, true, false]));
}

#[test]
fn debug_lists_flags() {
    check!(r#"format!("{:?}") of SYN | ACK and of empty()"#, format!("{:?} {:?}", TcpFlags::ACK | TcpFlags::SYN, TcpFlags::empty()), "TcpFlags(SYN | ACK) TcpFlags(empty)");
}

#[test]
fn not_stays_in_six_bits() {
    check!(r#"(!TcpFlags::SYN).bits()"#, (!TcpFlags::SYN).bits(), 0x3D);
}

#[test]
fn from_bits_rejects_unknown() {
    check!(r#"from_bits(0x12), from_bits(0x40), from_bits_truncate(0xFF)"#, (TcpFlags::from_bits(0x12), TcpFlags::from_bits(0x40), TcpFlags::from_bits_truncate(0xFF)), (Some(TcpFlags::SYN | TcpFlags::ACK), None, TcpFlags::all()));
}

#[test]
fn valid_table() {
    check!(r#"VALID[SYN], VALID[SYN | FIN], VALID[ACK | PSH]"#, (VALID[0x02], VALID[0x03], VALID[0x18]), (true, false, true));
}
