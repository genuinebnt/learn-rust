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

#[test]
fn oldest_and_snapshot() {
    let mut pa = ProcArray::new(4);
    for s in 0..3 {
        pa.connect(s, 100 + s as u32, 1, "app", 0);
    }
    pa.begin(0, 120, 5);
    pa.set_xmin(1, 90);
    pa.begin(2, 110, 6);
    let mut xip = Vec::new();
    check!(r#"xids 120 (slot 0) and 110 (slot 2), xmin 90 (slot 1); oldest_xmin(200), snapshot(200)"#, (pa.oldest_xmin(200), pa.snapshot(200, &mut xip), xip.clone()), (90, 110, vec![110, 120]));
}

#[test]
fn end_clears_both() {
    let mut pa = ProcArray::new(1);
    pa.connect(0, 7, 1, "psql", 0);
    pa.begin(0, 50, 3);
    pa.set_xmin(0, 40);
    pa.end(0);
    let mut xip = vec![1, 2, 3];
    check!(r#"slot 0 runs xid 50 with xmin 40, then ends"#, (pa.oldest_xmin(99), pa.snapshot(99, &mut xip), xip.len(), pa.xact_start(0)), (99, 99, 0, None));
}

#[test]
fn cold_fields() {
    let mut pa = ProcArray::new(2);
    pa.connect(1, 4242, 3, "reporting", 10);
    pa.begin(1, 77, 12);
    pa.set_query(1, "SELECT count(*) FROM orders");
    check!(r#"connect slot 1 as "reporting" at t=10, begin at t=12, set_query"#, (pa.pid(1), pa.application(1), pa.query(1), pa.xact_start(1), pa.pid(0), pa.connected()), (Some(4242), Some("reporting"), Some("SELECT count(*) FROM orders"), Some(12), None, 1));
}

#[test]
fn disconnect_forgets() {
    let mut pa = ProcArray::new(1);
    pa.connect(0, 1, 1, "x", 0);
    pa.begin(0, 5, 0);
    pa.set_xmin(0, 3);
    pa.disconnect(0);
    check!(r#"slot 0 in xid 5 with xmin 3 disconnects"#, (pa.oldest_xmin(10), pa.pid(0), pa.connected()), (10, None, 0));
}

#[test]
fn oldest_xmin_is_4x_faster() {
    let (pa, wide) = busy(1 << 17);
    let next = 2_000_000;
    anneal_prelude::assert_faster("oldest_xmin, 131072 backends", 4.0, 15, || wide_oldest_xmin(&wide, next), || pa.oldest_xmin(next));
    check!("oldest_xmin(2000000) over 131072 backends", pa.oldest_xmin(next), wide_oldest_xmin(&wide, next));
}
