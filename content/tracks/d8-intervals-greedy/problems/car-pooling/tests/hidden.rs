use solution::*;

#[test]
fn exactly_full() {
    check!(r#"trips = [(4, 0, 10)], capacity = 4"#, car_pooling(&[(4, 0, 10)], 4), true);
}

#[test]
fn zero_capacity() {
    check!(r#"trips = [(1, 0, 1)], capacity = 0"#, car_pooling(&[(1, 0, 1)], 0), false);
}

#[test]
fn far_stops() {
    check!(r#"trips = [(1, 0, 1000000000), (1, 999999999, 1000000000)], capacity = 1"#, car_pooling(&[(1, 0, 1_000_000_000), (1, 999_999_999, 1_000_000_000)], 1), false);
}

#[test]
fn three_at_one_point() {
    check!(r#"trips = [(1, 0, 10), (1, 5, 6), (1, 5, 7)], capacity = 2"#, car_pooling(&[(1, 0, 10), (1, 5, 6), (1, 5, 7)], 2), false);
}

#[test]
fn relay() {
    check!(r#"trips = [(2, 0, 3), (2, 3, 6), (2, 6, 9)], capacity = 2"#, car_pooling(&[(2, 0, 3), (2, 3, 6), (2, 6, 9)], 2), true);
}

#[test]
fn unsorted_trips() {
    check!(r#"trips = [(2, 6, 9), (3, 0, 7)], capacity = 4"#, car_pooling(&[(2, 6, 9), (3, 0, 7)], 4), false);
}

#[test]
fn same_trip_twice() {
    check!(r#"trips = [(2, 1, 4), (2, 1, 4)], capacity = 4"#, car_pooling(&[(2, 1, 4), (2, 1, 4)], 4), true);
}

#[test]
fn big_capacity() {
    check!(r#"trips = [(1000, 0, 1); 1000], capacity = 1000000"#, car_pooling(&vec![(1000, 0, 1); 1000], 1_000_000), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(813);
    for _ in 0..400 {
        let n = rng.below(7);
        let trips: Vec<(u32, u32, u32)> = (0..n)
            .map(|_| {
                let people = rng.int(1, 5) as u32;
                let from = rng.int(0, 10) as u32;
                let len = rng.int(1, 5) as u32;
                (people, from, from + len)
            })
            .collect();
        let capacity = rng.int(0, 12) as u32;
        let want = (0..=15u32).all(|x| trips.iter().filter(|t| t.1 <= x && x < t.2).map(|t| t.0).sum::<u32>() <= capacity);
        check!(format!("trips = {trips:?}, capacity = {capacity}"), car_pooling(&trips, capacity), want);
    }
}

#[test]
fn scale_100k() {
    let trips: Vec<(u32, u32, u32)> = (0..100_000u32).rev().map(|i| (1, i * 10_000, i * 10_000 + 5_000_000)).collect();
    check!("(1, 10000i, 10000i + 5000000) for i in 0..100000, capacity 500 and 499", (car_pooling(&trips, 500), car_pooling(&trips, 499)), (true, false));
}
