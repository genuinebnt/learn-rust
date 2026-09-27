use solution::*;

/// The array-of-PGPROCs baseline, as the starter lays it out.
#[derive(Clone)]
struct Wide {
    connected: bool,
    pid: u32,
    database: u32,
    xid: u32,
    xmin: u32,
    wait_event: u32,
    backend_start: u64,
    xact_start: u64,
    app_len: u8,
    application_name: [u8; 64],
    client_addr: [u8; 16],
    query_len: u8,
    query: [u8; 128],
}

fn wide_oldest_xmin(procs: &[Wide], next_xid: u32) -> u32 {
    let mut oldest = next_xid;
    for p in procs {
        if !p.connected {
            continue;
        }
        if p.xid != 0 && p.xid < oldest {
            oldest = p.xid;
        }
        if p.xmin != 0 && p.xmin < oldest {
            oldest = p.xmin;
        }
    }
    oldest
}

/// `n` connected backends; every 50th is in a transaction and every 20th holds a snapshot.
fn busy(n: usize) -> (ProcArray, Vec<Wide>) {
    let mut pa = ProcArray::new(n);
    let blank = Wide { connected: true, pid: 0, database: 5, xid: 0, xmin: 0, wait_event: 0, backend_start: 0, xact_start: 0, app_len: 0, application_name: [0; 64], client_addr: [0; 16], query_len: 0, query: [0; 128] };
    let mut wide = vec![blank; n];
    for slot in 0..n {
        pa.connect(slot, 1000 + slot as u32, 5, "pgbench", 1);
        wide[slot].pid = 1000 + slot as u32;
        if slot % 50 == 0 {
            let xid = 1_000_000 + ((slot * 7919) % 100_000) as u32;
            pa.begin(slot, xid, 2);
            wide[slot].xid = xid;
        }
        if slot % 20 == 0 {
            let xmin = 900_000 + ((slot * 104_729) % 100_000) as u32;
            pa.set_xmin(slot, xmin);
            wide[slot].xmin = xmin;
        }
    }
    (pa, wide)
}

/// The proc array as plain per-slot records.
#[derive(Clone, Default, Debug)]
struct Slot {
    connected: bool,
    pid: u32,
    app: String,
    query: String,
    xid: u32,
    xmin: u32,
    xact_start: u64,
}

#[test]
fn snapshot_is_faster_too() {
    let (pa, wide) = busy(1 << 17);
    let mut xip = Vec::with_capacity(4096);
    let mut wide_xip: Vec<u32> = Vec::with_capacity(4096);
    let mut wide_snapshot = |next: u32| {
        wide_xip.clear();
        wide_xip.extend(wide.iter().filter(|p| p.connected && p.xid != 0).map(|p| p.xid));
        wide_xip.sort_unstable();
        wide_xip.first().copied().unwrap_or(next)
    };
    let want = wide_snapshot(2_000_000);
    anneal_prelude::assert_faster("snapshot, 131072 backends", 2.0, 15, || wide_snapshot(2_000_000), || pa.snapshot(2_000_000, &mut xip));
    check!("snapshot(2000000): xmin and the number of running xids", (pa.snapshot(2_000_000, &mut xip), xip.len()), (want, 2622));
}

#[test]
fn next_xid_caps() {
    let mut pa = ProcArray::new(1);
    pa.connect(0, 1, 1, "x", 0);
    pa.begin(0, 500, 0);
    let mut xip = Vec::new();
    check!(r#"xid 500 running; oldest_xmin(300), snapshot(300)"#, (pa.oldest_xmin(300), pa.snapshot(300, &mut xip)), (300, 300));
}

#[test]
fn no_backends() {
    let pa = ProcArray::new(3);
    let mut xip = Vec::new();
    check!(r#"ProcArray::new(0) and new(3) with nobody connected"#, (ProcArray::new(0).oldest_xmin(9), pa.oldest_xmin(9), pa.snapshot(9, &mut xip), pa.connected()), (9, 9, 9, 0));
}

#[test]
fn reconnect_is_clean() {
    let mut pa = ProcArray::new(1);
    pa.connect(0, 1, 1, "a", 0);
    pa.begin(0, 8, 1);
    pa.set_query(0, "VACUUM");
    pa.disconnect(0);
    pa.connect(0, 2, 1, "b", 2);
    check!(r#"slot 0: connect, begin 8, set_query, disconnect, connect again as "b""#, (pa.application(0), pa.query(0), pa.xact_start(0), pa.oldest_xmin(20)), (Some("b"), Some(""), None, 20));
}

#[test]
fn names_are_cut() {
    let mut pa = ProcArray::new(1);
    pa.connect(0, 1, 1, &"x".repeat(70), 0);
    pa.set_query(0, &"é".repeat(100));
    check!(r#"a 70-byte application name and a 200-byte query of 'é' (2 bytes each)"#, (pa.application(0).map(str::len), pa.query(0).map(|q| (q.len(), q.chars().count()))), (Some(64), Some((128, 64))));
}

#[test]
fn xmin_only_holder() {
    let mut pa = ProcArray::new(1);
    pa.connect(0, 1, 1, "x", 0);
    pa.set_xmin(0, 42);
    let mut xip = Vec::new();
    check!(r#"a backend with a snapshot but no xid"#, (pa.oldest_xmin(100), pa.snapshot(100, &mut xip), pa.xact_start(0)), (42, 100, None));
}

#[test]
fn big_array_correct() {
    let (pa, wide) = busy(10_000);
    check!(r#"busy(10000): oldest_xmin vs the wide scan"#, pa.oldest_xmin(2_000_000), wide_oldest_xmin(&wide, 2_000_000));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(8215);
    for _ in 0..150 {
        let n = 1 + rng.below(8);
        let mut pa = ProcArray::new(n);
        let mut model = vec![Slot::default(); n];
        let mut next_xid = 100u32;
        let mut log = Vec::new();
        let mut xip = vec![7, 7, 7];
        for now in 1..=30u64 {
            let slot = rng.below(n);
            let m = &mut model[slot];
            match rng.below(6) {
                0 if !m.connected => {
                    let app_len = rng.below(3) * 30;
                    let app = rng.string(app_len, "abc-_é");
                    log.push(format!("connect({slot}, app of {} bytes)", app.len()));
                    pa.connect(slot, 500 + slot as u32, 1, &app, now);
                    let mut cut = app.clone();
                    while cut.len() > 64 {
                        cut.pop();
                    }
                    *m = Slot { connected: true, pid: 500 + slot as u32, app: cut, ..Slot::default() };
                }
                1 if m.connected => {
                    log.push(format!("disconnect({slot})"));
                    pa.disconnect(slot);
                    *m = Slot::default();
                }
                2 if m.connected && m.xid == 0 => {
                    next_xid += 1 + rng.below(3) as u32;
                    log.push(format!("begin({slot}, {next_xid})"));
                    pa.begin(slot, next_xid, now);
                    m.xid = next_xid;
                    m.xact_start = now;
                }
                3 if m.connected => {
                    let xmin = next_xid - rng.below(20) as u32;
                    log.push(format!("set_xmin({slot}, {xmin})"));
                    pa.set_xmin(slot, xmin);
                    m.xmin = xmin;
                }
                4 if m.connected => {
                    log.push(format!("end({slot})"));
                    pa.end(slot);
                    m.xid = 0;
                    m.xmin = 0;
                    m.xact_start = 0;
                }
                _ if m.connected => {
                    let q = format!("SELECT {now}");
                    log.push(format!("set_query({slot}, {q:?})"));
                    pa.set_query(slot, &q);
                    m.query = q;
                }
                _ => {}
            }
            let ctx = log.join(", ");
            let next = next_xid + 1;
            let live = model.iter().filter(|s| s.connected);
            let want_oldest = live.flat_map(|s| [s.xid, s.xmin]).filter(|&x| x != 0).fold(next, u32::min);
            check!(format!("{ctx}: oldest_xmin({next})"), pa.oldest_xmin(next), want_oldest);
            let mut want_xip: Vec<u32> = model.iter().filter(|s| s.connected && s.xid != 0).map(|s| s.xid).collect();
            want_xip.sort();
            let xmin = pa.snapshot(next, &mut xip);
            check!(format!("{ctx}: snapshot({next})"), (xmin, xip.clone()), (want_xip.first().copied().unwrap_or(next), want_xip));
            for (i, s) in model.iter().enumerate() {
                let want = (s.connected.then_some(s.pid), s.connected.then(|| s.app.clone()), s.connected.then(|| s.query.clone()), (s.xid != 0).then_some(s.xact_start));
                check!(format!("{ctx}: slot {i}"), (pa.pid(i), pa.application(i).map(String::from), pa.query(i).map(String::from), pa.xact_start(i)), want);
            }
            check!(format!("{ctx}: connected()"), pa.connected(), model.iter().filter(|s| s.connected).count());
        }
    }
}
