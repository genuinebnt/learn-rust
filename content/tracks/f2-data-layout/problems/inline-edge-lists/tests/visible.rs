use solution::*;

#[test]
fn block_fits_56_bytes() {
    check!(r#"size_of::<Block>() <= 56"#, std::mem::size_of::<Block>() <= 56, true);
}

/// `groups` copies of: a block switching 4 ways, the 4 arms, and a join block with 4 predecessors that
/// falls through to the next group.
fn switches(cfg: &mut Cfg, groups: usize) {
    let mut prev: Option<BlockId> = None;
    for _ in 0..groups {
        let head = cfg.add_block(3);
        if let Some(p) = prev {
            cfg.add_edge(p, head);
        }
        let join = cfg.add_block(1);
        for _ in 0..4 {
            let arm = cfg.add_block(2);
            cfg.add_edge(head, arm);
            cfg.add_edge(arm, join);
        }
        prev = Some(join);
    }
}

fn ids(xs: &[BlockId]) -> Vec<usize> {
    xs.iter().map(|b| b.0 as usize).collect()
}

#[test]
fn small_blocks_dont_allocate() {
    let mut cfg = Cfg::with_capacity(6000);
    let (_, n) = anneal_prelude::allocs(|| switches(&mut cfg, 1000));
    check!(r#"Cfg::with_capacity(6000), then 1000 four-way switches: allocations"#, (n.count, cfg.len(), cfg.succs(BlockId(0)).len(), cfg.preds(BlockId(1)).len()), (0, 6000, 4, 4));
}

#[test]
fn split_one_critical_edge() {
    let mut cfg = Cfg::new();
    for s in [4, 2, 7] {
        cfg.add_block(s);
    }
    cfg.add_edge(BlockId(0), BlockId(1));
    cfg.add_edge(BlockId(0), BlockId(2));
    cfg.add_edge(BlockId(1), BlockId(2));
    let count = cfg.split_critical_edges();
    check!(r#"0 -> 1, 0 -> 2, 1 -> 2; split"#, (count, ids(cfg.succs(BlockId(0))), ids(cfg.preds(BlockId(2))), ids(cfg.succs(BlockId(3))), ids(cfg.preds(BlockId(3))), cfg.stmts(BlockId(3))), (1, vec![1, 3], vec![3, 1], vec![2], vec![0], 0));
}

#[test]
fn diamond_has_none() {
    let mut cfg = Cfg::new();
    for _ in 0..4 {
        cfg.add_block(1);
    }
    for (a, b) in [(0, 1), (0, 2), (1, 3), (2, 3)] {
        cfg.add_edge(BlockId(a), BlockId(b));
    }
    check!(r#"a diamond 0 -> {1, 2} -> 3: split"#, (cfg.split_critical_edges(), cfg.len()), (0, 4));
}

#[test]
fn big_switch_spills() {
    let mut cfg = Cfg::new();
    for _ in 0..10 {
        cfg.add_block(0);
    }
    for b in 1..=9 {
        cfg.add_edge(BlockId(0), BlockId(b));
    }
    check!(r#"block 0 switching to 9 blocks"#, (ids(cfg.succs(BlockId(0))), cfg.preds(BlockId(9)).to_vec()), ((1..=9).collect::<Vec<usize>>(), vec![BlockId(0)]));
}
