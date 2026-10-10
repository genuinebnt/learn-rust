//! The SQL tests of BusTub's `test/sql/` that need only expressions: `lower`/`upper` (`p0.01`..`p0.03`), arithmetic and comparison on
//! constants (`baby_arithmetic.slt`) and plain scans of the mock tables (`intro.slt`). Each file is run by `tests/slt/mod.rs`.

mod slt;

#[test]
fn p0_01_lower_upper() {
    slt::run_slt("p0.01-lower-upper.slt", 128);
}

#[test]
fn p0_02_function_error() {
    slt::run_slt("p0.02-function-error.slt", 128);
}

#[test]
fn p0_03_string_scan() {
    slt::run_slt("p0.03-string-scan.slt", 128);
}

#[test]
fn baby_arithmetic() {
    slt::run_slt("baby_arithmetic.slt", 128);
}

#[test]
fn intro() {
    slt::run_slt("intro.slt", 128);
}
