use solution::*;

fn particle(i: u64, pos: [f32; 3], vel: [f32; 3]) -> Particle {
    let mut tag = [0u8; 32];
    tag[..8].copy_from_slice(&i.to_le_bytes());
    Particle { id: i, pos, vel, mass: 1.0 + (i % 5) as f32, charge: -1.0, radius: 0.5, temperature: 300.0, species: (i % 3) as u32, flags: i as u32, tag }
}

/// The same step, as an array of structs: the baseline.
fn step_aos(ps: &mut [Particle], dt: f32) {
    for p in ps {
        p.vel[2] -= G * dt;
        p.pos[0] += p.vel[0] * dt;
        p.pos[1] += p.vel[1] * dt;
        p.pos[2] += p.vel[2] * dt;
    }
}

fn cloud(n: usize) -> Vec<Particle> {
    (0..n as u64).map(|i| particle(i, [(i % 100) as f32, (i % 37) as f32, (i % 11) as f32], [1.0, -0.5, (i % 7) as f32 - 3.0])).collect()
}

#[test]
fn count_below_is_6x_faster() {
    let n = 1 << 20;
    let baseline = cloud(n);
    let mut ps = Particles::with_capacity(n);
    for p in &baseline {
        ps.push(*p);
    }
    let aos = |ps: &[Particle]| ps.iter().filter(|p| p.pos[2] < 5.0).count();
    anneal_prelude::assert_faster("count_below, 1048576 particles", 6.0, 15, || aos(&baseline), || ps.count_below(5.0));
    check!("count_below(5.0)", ps.count_below(5.0), aos(&baseline));
}

#[test]
fn empty() {
    let mut ps = Particles::with_capacity(0);
    ps.step(1.0);
    check!(r#"no particles: len, count_below, kinetic_energy, step"#, (ps.len(), ps.is_empty(), ps.count_below(0.0), ps.kinetic_energy()), (0, true, 0, 0.0));
}

#[test]
fn zero_dt() {
    let p = particle(3, [1.0, 2.0, 3.0], [4.0, 5.0, 6.0]);
    let mut ps = Particles::with_capacity(1);
    ps.push(p);
    ps.step(0.0);
    check!(r#"step(0.0) leaves everything as it was"#, ps.get(0) == p, true);
}

#[test]
fn backwards_step() {
    let mut ps = Particles::with_capacity(1);
    ps.push(particle(0, [0.0; 3], [0.0; 3]));
    ps.step(0.5);
    ps.step(-0.5);
    check!(r#"step(0.5) then step(-0.5) from rest at z = 0"#, (ps.get(0).vel[2], ps.get(0).pos[2]), (0.0, -G * 0.5 * 0.5));
}

#[test]
fn boundary_not_below() {
    let mut ps = Particles::with_capacity(1);
    ps.push(particle(0, [0.0, 0.0, 2.5], [0.0; 3]));
    check!(r#"z exactly at the ground"#, ps.count_below(2.5), 0);
}

#[test]
fn push_after_step() {
    let b = particle(9, [1.0; 3], [1.0; 3]);
    let mut ps = Particles::with_capacity(1);
    ps.push(particle(8, [0.0; 3], [0.0; 3]));
    ps.step(0.25);
    ps.push(b);
    check!(r#"push a, step, push b: b is untouched"#, (ps.get(1) == b, ps.len()), (true, 2));
}

#[test]
#[should_panic]
fn get_out_of_range_panics() {
    Particles::with_capacity(0).get(0);
}

#[test]
fn many_steps_match() {
    let mut model = cloud(1000);
    let mut ps = Particles::with_capacity(1000);
    for p in &model {
        ps.push(*p);
    }
    for _ in 0..20 {
        ps.step(0.01);
        step_aos(&mut model, 0.01);
    }
    check!(r#"1000 particles, 20 steps of 0.01"#, (0..1000).all(|i| ps.get(i) == model[i]), true);
}

#[test]
fn random_steps_vs_aos() {
    let mut rng = anneal_prelude::Rng::new(8214);
    for _ in 0..100 {
        let n = rng.below(40);
        let mut model = Vec::new();
        for i in 0..n as u64 {
            let pos = [rng.int(-100, 100) as f32 / 4.0, rng.int(-100, 100) as f32 / 4.0, rng.int(-100, 100) as f32 / 4.0];
            let vel = [rng.int(-40, 40) as f32 / 8.0, rng.int(-40, 40) as f32 / 8.0, rng.int(-40, 40) as f32 / 8.0];
            model.push(particle(i, pos, vel));
        }
        let mut ps = Particles::with_capacity(n);
        for p in &model {
            ps.push(*p);
        }
        let steps = rng.below(5);
        let dt = rng.int(1, 100) as f32 / 1000.0;
        for _ in 0..steps {
            ps.step(dt);
            step_aos(&mut model, dt);
        }
        let ground = rng.int(-20, 20) as f32;
        let ctx = format!("{n} particles, {steps} steps of dt = {dt}");
        check!(format!("{ctx}: every get(i)"), (0..n).map(|i| ps.get(i)).collect::<Vec<_>>(), model.clone());
        check!(format!("{ctx}: count_below({ground})"), ps.count_below(ground), model.iter().filter(|p| p.pos[2] < ground).count());
        let want: f64 = model.iter().map(|p| 0.5 * p.mass as f64 * p.vel.iter().map(|&v| v as f64 * v as f64).sum::<f64>()).sum();
        check!(format!("{ctx}: kinetic_energy within 1e-9 relative"), (ps.kinetic_energy() - want).abs() <= 1e-9 * want.abs().max(1.0), true);
    }
}
