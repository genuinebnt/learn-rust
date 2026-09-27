use solution::*;

/// Test-defined units: `Inches` derives nothing; `Handle` holds a raw pointer, so it's neither Send nor Sync.
#[allow(dead_code)]
struct Inches;

#[allow(dead_code)]
impl Unit for Inches {
    const METERS: f64 = 0.0254;
    const SYMBOL: &'static str = "in";
}

#[allow(dead_code)]
struct Handle(*const u8);

#[allow(dead_code)]
impl Unit for Handle {
    const METERS: f64 = 2.0;
    const SYMBOL: &'static str = "h";
}

/// Compile-time facts as runtime booleans: an inherent const wins over the trait's when its bounds hold.
#[allow(dead_code)]
struct Probe<A, B = ()>(std::marker::PhantomData<(A, B)>);

#[allow(dead_code)]
trait Fallback {
    const ADDS: bool = false;
    const SEND_SYNC: bool = false;
}

#[allow(dead_code)]
impl<A, B> Fallback for Probe<A, B> {}

#[allow(dead_code)]
impl<A: std::ops::Add<B>, B> Probe<A, B> {
    const ADDS: bool = true;
}

#[allow(dead_code)]
impl<A: Send + Sync> Probe<A> {
    const SEND_SYNC: bool = true;
}

#[allow(dead_code)]
fn close(a: f64, b: f64) -> bool {
    (a - b).abs() < 1e-9 * b.abs().max(1.0)
}

#[test]
fn same_unit_adds() {
    check!(r#"2.5 m + 1 m"#, (Length::<Meters>::new(2.5) + Length::<Meters>::new(1.0)).value(), 3.5);
}

#[test]
fn mixed_units_dont_add() {
    check!(r#"does Length<Meters> + Length<Feet> compile? and Meters + Meters?"#, (Probe::<Length<Meters>, Length<Feet>>::ADDS, Probe::<Length<Meters>, Length<Meters>>::ADDS), (false, true));
}

#[test]
fn convert_then_add() {
    check!(r#"1 km + 500 m, in metres"#, close((Length::<Kilometers>::new(1.0).to::<Meters>() + Length::<Meters>::new(500.0)).value(), 1500.0), true);
}

#[test]
fn copy_for_any_unit() {
    let a = Length::<Inches>::new(2.5);
    check!(r#"Inches (no derives): a + a, compare, Debug"#, (a + a == Length::new(5.0), a < a * 2.0, format!("{a:?}")), (true, true, "2.5 in".to_string()));
}

#[test]
fn send_sync_for_any_unit() {
    check!(r#"is Length<Handle> Send + Sync?"#, (Probe::<Length<Handle>>::SEND_SYNC, Probe::<Length<Meters>>::SEND_SYNC), (true, true));
}
