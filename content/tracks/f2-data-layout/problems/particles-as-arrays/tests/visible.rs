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
fn one_step() {
    let mut ps = Particles::with_capacity(1);
    ps.push(particle(7, [0.0, 0.0, 10.0], [1.0, 0.0, 0.0]));
    ps.step(0.1);
    let q = ps.get(0);
    check!(r#"one step of dt = 0.1 for pos [0, 0, 10], vel [1, 0, 0]"#, (q.vel, q.pos), ([1.0, 0.0, -G * 0.1], [0.1, 0.0, 10.0 + (-G * 0.1) * 0.1]));
}

#[test]
fn get_keeps_cold_fields() {
    let p = particle(42, [1.0, 2.0, 3.0], [4.0, 5.0, 6.0]);
    let mut ps = Particles::with_capacity(1);
    ps.push(p);
    check!(r#"push particle 42, get it back"#, ps.get(0) == p, true);
}

#[test]
fn count_below_ground() {
    let mut ps = Particles::with_capacity(4);
    for (i, z) in [5.0, -1.0, 0.0, -3.0].into_iter().enumerate() {
        ps.push(particle(i as u64, [0.0, 0.0, z], [0.0; 3]));
    }
    check!(r#"z = 5, -1, 0, -3: count_below(0.0)"#, ps.count_below(0.0), 2);
}

#[test]
fn kinetic_energy() {
    let mut ps = Particles::with_capacity(2);
    ps.push(Particle { mass: 1.0, ..particle(0, [0.0; 3], [2.0, 0.0, 0.0]) });
    ps.push(Particle { mass: 2.0, ..particle(1, [0.0; 3], [0.0, -1.0, 0.0]) });
    check!(r#"mass 1 at |v| = 2, mass 2 at |v| = 1"#, ps.kinetic_energy(), 3.0);
}

#[test]
fn step_is_faster() {
    let n = 1 << 18;
    let mut baseline = cloud(n);
    let mut ps = Particles::with_capacity(n);
    for p in &baseline {
        ps.push(*p);
    }
    anneal_prelude::assert_faster("step, 262144 particles", 2.5, 15, || step_aos(&mut baseline, 0.001), || ps.step(0.001));
    check!("after the timed steps, particle 12345 matches the AoS copy", ps.get(12_345), baseline[12_345]);
}
