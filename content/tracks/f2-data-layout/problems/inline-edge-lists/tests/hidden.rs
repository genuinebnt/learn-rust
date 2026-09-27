use solution::*;

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
fn switch_graph_splits() {
    let mut cfg = Cfg::new();
    switches(&mut cfg, 1);
    check!(r#"one four-way switch group, split: none of its edges is critical"#, (cfg.split_critical_edges(), cfg.len()), (0, 6));
}

#[test]
fn loop_back_edge() {
    let mut cfg = Cfg::new();
    for _ in 0..3 {
        cfg.add_block(1);
    }
    for (a, b) in [(0, 1), (1, 1), (1, 2)] {
        cfg.add_edge(BlockId(a), BlockId(b));
    }
    let count = cfg.split_critical_edges();
    check!(r#"0 -> 1, 1 -> 1, 1 -> 2: the self-loop is critical"#, (count, ids(cfg.succs(BlockId(1))), ids(cfg.preds(BlockId(1))), ids(cfg.succs(BlockId(3)))), (1, vec![3, 2], vec![0, 3], vec![1]));
}

#[test]
fn duplicate_edges_ignored() {
    let mut cfg = Cfg::new();
    cfg.add_block(0);
    cfg.add_block(0);
    for _ in 0..3 {
        cfg.add_edge(BlockId(0), BlockId(1));
    }
    check!(r#"0 -> 1 added three times"#, (ids(cfg.succs(BlockId(0))), ids(cfg.preds(BlockId(1)))), (vec![1], vec![0]));
}

#[test]
fn rpo_skips_unreachable() {
    let mut cfg = Cfg::new();
    for _ in 0..4 {
        cfg.add_block(0);
    }
    for (a, b) in [(0, 2), (2, 3), (1, 3)] {
        cfg.add_edge(BlockId(a), BlockId(b));
    }
    check!(r#"0 -> 2, 2 -> 3, 1 -> 3 from 0"#, ids(&cfg.reverse_postorder(BlockId(0))), vec![0, 2, 3]);
}

#[test]
fn split_order() {
    let mut cfg = Cfg::new();
    for _ in 0..4 {
        cfg.add_block(0);
    }
    for (a, b) in [(0, 2), (0, 3), (1, 3), (1, 2)] {
        cfg.add_edge(BlockId(a), BlockId(b));
    }
    let count = cfg.split_critical_edges();
    check!(r#"0 -> {2, 3}, 1 -> {3, 2}: new blocks in (block, successor) order"#, (count, ids(cfg.succs(BlockId(0))), ids(cfg.succs(BlockId(1))), ids(cfg.preds(BlockId(2))), ids(cfg.preds(BlockId(3)))), (4, vec![4, 5], vec![6, 7], vec![4, 7], vec![5, 6]));
}

#[test]
fn empty_cfg() {
    let mut cfg = Cfg::new();
    check!(r#"Cfg::new()"#, (cfg.len(), cfg.is_empty(), cfg.split_critical_edges()), (0, true, 0));
}

#[test]
fn stmts_kept() {
    let mut cfg = Cfg::new();
    let a = cfg.add_block(5);
    let b = cfg.add_block(9);
    check!(r#"blocks with 5 and 9 statements"#, (cfg.stmts(a), cfg.stmts(b), cfg.succs(a).is_empty()), (5, 9, true));
}

#[test]
fn big_join() {
    let mut cfg = Cfg::new();
    for _ in 0..11 {
        cfg.add_block(0);
    }
    for b in 0..10 {
        cfg.add_edge(BlockId(b), BlockId(10));
    }
    check!(r#"10 blocks all jumping to block 10, then split"#, (cfg.preds(BlockId(10)).len(), cfg.split_critical_edges()), (10, 0));
}

/// The same graph as plain adjacency lists, with the same algorithms.
struct Model {
    succs: Vec<Vec<usize>>,
    preds: Vec<Vec<usize>>,
}

impl Model {
    fn edge(&mut self, a: usize, b: usize) {
        if !self.succs[a].contains(&b) {
            self.succs[a].push(b);
            self.preds[b].push(a);
        }
    }

    fn split(&mut self) -> usize {
        let n = self.succs.len();
        let mut count = 0;
        for a in 0..n {
            if self.succs[a].len() < 2 {
                continue;
            }
            for i in 0..self.succs[a].len() {
                let b = self.succs[a][i];
                if self.preds[b].len() < 2 {
                    continue;
                }
                let mid = self.succs.len();
                self.succs.push(vec![b]);
                self.preds.push(vec![a]);
                self.succs[a][i] = mid;
                let at = self.preds[b].iter().position(|&p| p == a).unwrap();
                self.preds[b][at] = mid;
                count += 1;
            }
        }
        count
    }

    fn rpo(&self, entry: usize) -> Vec<usize> {
        fn dfs(m: &Model, b: usize, seen: &mut Vec<bool>, post: &mut Vec<usize>) {
            seen[b] = true;
            for &s in &m.succs[b] {
                if !seen[s] {
                    dfs(m, s, seen, post);
                }
            }
            post.push(b);
        }
        let mut seen = vec![false; self.succs.len()];
        let mut post = Vec::new();
        dfs(self, entry, &mut seen, &mut post);
        post.reverse();
        post
    }
}

#[test]
fn random_vs_adjacency_lists() {
    let mut rng = anneal_prelude::Rng::new(8206);
    for _ in 0..200 {
        let n = 1 + rng.below(9);
        let mut cfg = Cfg::new();
        let mut model = Model { succs: vec![Vec::new(); n], preds: vec![Vec::new(); n] };
        for i in 0..n {
            cfg.add_block(i as u32);
        }
        let mut log = Vec::new();
        for _ in 0..rng.below(3 * n) {
            let (a, b) = (rng.below(n), rng.below(n));
            log.push(format!("{a}->{b}"));
            cfg.add_edge(BlockId(a as u32), BlockId(b as u32));
            model.edge(a, b);
        }
        let ctx = format!("{n} blocks, edges [{}]", log.join(", "));
        check!(format!("{ctx}: reverse_postorder(0)"), ids(&cfg.reverse_postorder(BlockId(0))), model.rpo(0));
        let got = cfg.split_critical_edges();
        let want = model.split();
        check!(format!("{ctx}: split_critical_edges()"), (got, cfg.len()), (want, model.succs.len()));
        for b in 0..model.succs.len() {
            let id = BlockId(b as u32);
            check!(format!("{ctx}: after splitting, succs and preds of {b}"), (ids(cfg.succs(id)), ids(cfg.preds(id))), (model.succs[b].clone(), model.preds[b].clone()));
        }
        check!(format!("{ctx}: after splitting, reverse_postorder(0)"), ids(&cfg.reverse_postorder(BlockId(0))), model.rpo(0));
    }
}
