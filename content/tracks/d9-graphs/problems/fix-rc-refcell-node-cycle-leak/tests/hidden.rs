use solution::*;

#[test]
fn grandchild_freed() {
    let r = Node::root("r");
    let c = r.add_child("c");
    let g = c.add_child("g");
    let (wr, wg) = (std::rc::Rc::downgrade(&r), std::rc::Rc::downgrade(&g));
    drop(g);
    drop(c);
    drop(r);
    check!(r#"r → c → g; drop every handle"#, (wr.upgrade().is_none(), wg.upgrade().is_none()), (true, true));
}

#[test]
fn orphan() {
    let r = Node::root("r");
    let c = r.add_child("c");
    drop(r);
    check!(r#"keep the child, drop the root"#, c.parent_name(), None);
}

#[test]
fn only_one_strong_handle_to_the_root() {
    let r = Node::root("r");
    let _kids: Vec<_> = ["a", "b", "c"].into_iter().map(|n| r.add_child(n)).collect();
    check!(r#"root r with three children"#, std::rc::Rc::strong_count(&r), 1);
}

#[test]
fn grandchild_sees_its_parent() {
    let r = Node::root("r");
    let c = r.add_child("c");
    let g = c.add_child("g");
    check!(r#"r → c → g"#, (g.parent_name(), c.parent_name(), c.child_names()), (Some("c".to_string()), Some("r".to_string()), vec!["g".to_string()]));
}

#[test]
fn unicode_names() {
    let r = Node::root("根");
    let c = r.add_child("é");
    check!(r#"root "根" with child "é""#, (c.parent_name(), r.child_names()), (Some("根".to_string()), vec!["é".to_string()]));
}

#[test]
fn deep_chain_freed() {
    let r = Node::root("0");
    let mut cur = std::rc::Rc::clone(&r);
    for i in 1..100 {
        let next = cur.add_child(&i.to_string());
        cur = next;
    }
    let (wr, wleaf) = (std::rc::Rc::downgrade(&r), std::rc::Rc::downgrade(&cur));
    drop(cur);
    drop(r);
    check!(r#"a chain 100 levels deep; drop every handle"#, (wr.upgrade().is_none(), wleaf.upgrade().is_none()), (true, true));
}

#[test]
fn many_children_freed() {
    let r = Node::root("r");
    let weak: Vec<_> = (0..1000).map(|i| std::rc::Rc::downgrade(&r.add_child(&i.to_string()))).collect();
    drop(r);
    check!(r#"root with 1000 children; drop every handle"#, weak.iter().all(|w| w.upgrade().is_none()), true);
}

#[test]
fn child_kept_while_root_lives() {
    let r = Node::root("r");
    drop(r.add_child("c"));
    check!(r#"keep the root, drop the child handle, then ask the root"#, r.child_names().len(), 1);
}

#[test]
fn random_trees_vs_model() {
    let mut rng = anneal_prelude::Rng::new(958);
    for _ in 0..200 {
        let n = 1 + rng.below(12);
        let parent: Vec<usize> = (0..n).map(|i| if i == 0 { 0 } else { rng.below(i) }).collect();
        let mut nodes = vec![Node::root("n0")];
        for i in 1..n {
            let child = nodes[parent[i]].add_child(&format!("n{i}"));
            nodes.push(child);
        }
        let got: Vec<(Option<String>, Vec<String>)> = nodes.iter().map(|x| (x.parent_name(), x.child_names())).collect();
        // Model: the parent array itself.
        let want: Vec<(Option<String>, Vec<String>)> =
            (0..n).map(|i| ((i > 0).then(|| format!("n{}", parent[i])), (i + 1..n).filter(|&j| parent[j] == i).map(|j| format!("n{j}")).collect())).collect();
        let weak: Vec<_> = nodes.iter().map(std::rc::Rc::downgrade).collect();
        drop(nodes);
        let freed = weak.iter().all(|w| w.upgrade().is_none());
        check!(format!("parents = {parent:?}"), (got, freed), (want, true));
    }
}
