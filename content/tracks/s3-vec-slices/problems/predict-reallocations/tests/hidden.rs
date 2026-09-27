use solution::*;

#[test]
fn with_capacity_never_reallocates() {
    let mut v: Vec<u32> = Vec::with_capacity(100);
    let cap = v.capacity();
    v.extend(0..100u32);
    check!("Vec::with_capacity(100) then 100 pushes", (REALLOCATIONS > 0, v.capacity() == cap), (true, true));
}
