use solution::*;

#[test]
fn reallocation_count() {
    let mut v: Vec<u32> = Vec::new();
    let (mut changes, mut cap) = (0, v.capacity());
    for i in 0..100 {
        v.push(i);
        if v.capacity() != cap {
            changes += 1;
            cap = v.capacity();
        }
    }
    check!("push 0..100 into Vec::<u32>::new()", REALLOCATIONS, changes);
}

#[test]
fn final_capacity() {
    let mut v: Vec<u32> = Vec::new();
    v.extend(0..100u32);
    let mut w: Vec<u32> = Vec::new();
    for i in 0..100 {
        w.push(i);
    }
    check!("capacity after 100 pushes", FINAL_CAPACITY, w.capacity());
}

#[test]
fn some_reallocations() {
    check!(r#"REALLOCATIONS"#, REALLOCATIONS > 0, true);
}

#[test]
fn room_for_all_100() {
    check!(r#"FINAL_CAPACITY"#, FINAL_CAPACITY >= 100, true);
}

#[test]
fn capacity_is_a_power_of_two() {
    check!(r#"FINAL_CAPACITY"#, FINAL_CAPACITY.is_power_of_two(), true);
}
