use solution::*;

#[test]
fn empty() {
    check!(r#""""#, sum_csv(""), Ok(0));
}

#[test]
fn empty_fields_and_negatives() {
    check!(r#"" -4 ,, 10""#, sum_csv(" -4 ,, 10"), Ok(6));
}

#[test]
fn float_is_not_int() {
    check!(r#""1.5""#, sum_csv("1.5").is_err(), true);
}

#[test]
fn only_commas() {
    check!(r#"",,,""#, sum_csv(",,,"), Ok(0));
}

#[test]
fn only_spaces() {
    check!(r#""   ""#, sum_csv("   "), Ok(0));
}

#[test]
fn plus_sign() {
    check!(r#""+5,+6""#, sum_csv("+5,+6"), Ok(11));
}

#[test]
fn tabs_trimmed() {
    check!(r#""\t3\t,4\n""#, sum_csv("\t3\t,4\n"), Ok(7));
}

#[test]
fn space_inside_field() {
    check!(r#""1 2,3""#, sum_csv("1 2,3").is_err(), true);
}

#[test]
fn beyond_i32() {
    check!(r#""3000000000,3000000000""#, sum_csv("3000000000,3000000000"), Ok(6_000_000_000));
}

#[test]
fn i64_bounds() {
    check!(r#""9223372036854775807,-9223372036854775808""#, sum_csv("9223372036854775807,-9223372036854775808"), Ok(-1));
}

#[test]
fn too_big_for_i64() {
    check!(r#""9223372036854775808""#, sum_csv("9223372036854775808").is_err(), true);
}

#[test]
fn bad_field_last() {
    check!(r#""1,2,3,4,z""#, sum_csv("1,2,3,4,z").is_err(), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2202);
    let pieces = ["", " ", "7", " -3 ", "12", "x", "1e3", "0"];
    for _ in 0..400 {
        let n = rng.below(6);
        let mut fields = Vec::new();
        for _ in 0..n {
            fields.push(*rng.pick(&pieces));
        }
        let line = fields.join(",");
        let mut total = 0i64;
        let mut bad = false;
        for f in &fields {
            match f.trim() {
                "" => {}
                "7" => total += 7,
                "-3" => total -= 3,
                "12" => total += 12,
                "0" => {}
                _ => bad = true,
            }
        }
        check!(format!("line = {line:?}"), sum_csv(&line).ok(), if bad { None } else { Some(total) });
    }
}

#[test]
fn scale_200k_fields() {
    let line = "1, ".repeat(200_000);
    check!("line = \"1, 1, …\" (200000 fields)", sum_csv(&line), Ok(200_000));
}
