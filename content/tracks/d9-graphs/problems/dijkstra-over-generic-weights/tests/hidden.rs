use solution::*;

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
struct Cost {
    money: u32,
    hops: u32,
}

impl std::ops::Add for Cost {
    type Output = Cost;
    fn add(self, o: Cost) -> Cost {
        Cost { money: self.money + o.money, hops: self.hops + o.hops }
    }
}

impl Weight for Cost {
    const ZERO: Cost = Cost { money: 0, hops: 0 };
}

fn c(money: u32) -> Cost {
    Cost { money, hops: 1 }
}

#[test]
fn custom_weight_breaks_ties_on_hops() {
    check!(r#"Cost = (money, hops); 0→2 costs 5 directly or 2+3 via 1"#, dijkstra(&[vec![(1, c(2)), (2, c(5))], vec![(2, c(3))], vec![]], 0)[2], Some(Cost { money: 5, hops: 1 }));
}

#[test]
fn start_elsewhere() {
    check!(r#"adj = [[], [(0,7)]] as u32, src = 1"#, dijkstra(&[vec![], vec![(0, 7u32)]], 1), vec![Some(7), Some(0)]);
}
