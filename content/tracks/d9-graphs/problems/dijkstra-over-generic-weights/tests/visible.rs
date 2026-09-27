use solution::*;

#[test]
fn u32() {
    check!(r#"adj = [[(1,4), (2,1)], [(3,1)], [(1,2), (3,5)], []] as u32, src = 0"#, dijkstra(&[vec![(1, 4u32), (2, 1)], vec![(3, 1)], vec![(1, 2), (3, 5)], vec![]], 0), vec![Some(0), Some(3), Some(1), Some(4)]);
}

#[test]
fn unreachable_u64() {
    check!(r#"adj = [[(1,10)], [], []] as u64, src = 0"#, dijkstra(&[vec![(1, 10u64)], vec![], vec![]], 0), vec![Some(0), Some(10), None]);
}
