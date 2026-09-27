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
fn feet_to_meters() {
    check!(r#"10 ft in m"#, close(Length::<Feet>::new(10.0).to::<Meters>().value(), 3.048), true);
}

#[test]
fn inches_to_feet() {
    check!(r#"12 in in ft"#, close(Length::<Inches>::new(12.0).to::<Feet>().value(), 1.0), true);
}

#[test]
fn round_trip() {
    check!(r#"3.7 km -> ft -> km"#, close(Length::<Kilometers>::new(3.7).to::<Feet>().to::<Kilometers>().value(), 3.7), true);
}

#[test]
fn display() {
    check!(r#"Display of 2 ft and 0.5 km"#, (Length::<Feet>::new(2.0).to_string(), Length::<Kilometers>::new(0.5).to_string()), ("2 ft".to_string(), "0.5 km".to_string()));
}

#[test]
fn ratio() {
    check!(r#"3 m / 1.5 m"#, Length::<Meters>::new(3.0) / Length::<Meters>::new(1.5), 2.0);
}

#[test]
fn feet_and_km_dont_add() {
    check!(r#"Length<Feet> + Length<Kilometers>? Length<Inches> + Length<Inches>?"#, (Probe::<Length<Feet>, Length<Kilometers>>::ADDS, Probe::<Length<Inches>, Length<Inches>>::ADDS), (false, true));
}

#[test]
fn handle_lengths_work() {
    let h = Length::<Handle>::new(1.0);
    check!(r#"Length<Handle>: 1 h to m, and copy"#, (close(h.to::<Meters>().value(), 2.0), (h + h).value()), (true, 2.0));
}

#[test]
fn debug_of_feet() {
    check!(r#"{:?} of -1.5 ft"#, format!("{:?}", Length::<Feet>::new(-1.5)), "-1.5 ft");
}

#[test]
fn zero_sized_label() {
    check!(r#"size_of Length<Handle> and Length<Inches>"#, (std::mem::size_of::<Length<Handle>>(), std::mem::size_of::<Length<Inches>>()), (8, 8));
}

#[test]
fn scale_and_compare() {
    check!(r#"Inches: 3 * 2 vs 5"#, (Length::<Inches>::new(3.0) * 2.0 > Length::new(5.0), Length::<Inches>::new(3.0) == Length::new(3.0)), (true, true));
}

#[test]
fn random_conversions() {
    let mut rng = anneal_prelude::Rng::new(4517);
    for _ in 0..300 {
        let x = rng.int(-100_000, 100_000) as f64 / 100.0;
        let y = rng.int(-100_000, 100_000) as f64 / 100.0;
        let f = Length::<Feet>::new(x);
        let sum = (f.to::<Meters>() + Length::<Meters>::new(y)).value();
        check!(format!("{x} ft + {y} m"), (close(sum, x * 0.3048 + y), close(f.to::<Inches>().value(), x * 12.0), close(f.to::<Kilometers>().to::<Feet>().value(), x)), (true, true, true));
    }
}
