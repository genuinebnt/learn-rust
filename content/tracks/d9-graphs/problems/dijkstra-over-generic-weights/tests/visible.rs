use solution::*;

#[test]
fn u32() {
    check!(r#"adj = [[(1,4), (2,1)], [(3,1)], [(1,2), (3,5)], []] as u32, src = 0"#, dijkstra(&[vec![(1, 4u32), (2, 1)], vec![(3, 1)], vec![(1, 2), (3, 5)], vec![]], 0), vec![Some(0), Some(3), Some(1), Some(4)]);
}

#[test]
fn unreachable_u64() {
    check!(r#"adj = [[(1,10)], [], []] as u64, src = 0"#, dijkstra(&[vec![(1, 10u64)], vec![], vec![]], 0), vec![Some(0), Some(10), None]);
}

#[test]
fn single_node() {
    check!(r#"adj = [[]] as u32, src = 0"#, dijkstra::<u32>(&[vec![]], 0), vec![Some(0)]);
}

#[test]
fn parallel_edges_take_the_cheaper() {
    check!(r#"adj = [[(1,5), (1,2)], []] as u32, src = 0"#, dijkstra(&[vec![(1, 5u32), (1, 2)], vec![]], 0), vec![Some(0), Some(2)]);
}

#[test]
fn edges_are_directed() {
    check!(r#"adj = [[], [(0,1)]] as u32, src = 0"#, dijkstra(&[vec![], vec![(0, 1u32)]], 0), vec![Some(0), None]);
}
