/// Gravity, in m/s², along -z.
pub const G: f32 = 9.81;

/// A particle as checkpoints and the rest of the code see it.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Particle {
    pub id: u64,
    pub pos: [f32; 3],
    pub vel: [f32; 3],
    pub mass: f32,
    pub charge: f32,
    pub radius: f32,
    pub temperature: f32,
    pub species: u32,
    pub flags: u32,
    pub tag: [u8; 32],
}

#[derive(Clone, Copy)]
struct Hot {
    pos: [f32; 3],
    vel: [f32; 3],
    mass: f32,
}

#[derive(Clone, Copy)]
struct Cold {
    id: u64,
    charge: f32,
    radius: f32,
    temperature: f32,
    species: u32,
    flags: u32,
    tag: [u8; 32],
}

/// Hot fields split from cold ones, but still an array of structs.
pub struct Particles {
    hot: Vec<Hot>,
    cold: Vec<Cold>,
}

impl Particles {
    pub fn with_capacity(n: usize) -> Particles {
        Particles { hot: Vec::with_capacity(n), cold: Vec::with_capacity(n) }
    }

    pub fn push(&mut self, p: Particle) {
        self.hot.push(Hot { pos: p.pos, vel: p.vel, mass: p.mass });
        self.cold.push(Cold { id: p.id, charge: p.charge, radius: p.radius, temperature: p.temperature, species: p.species, flags: p.flags, tag: p.tag });
    }

    pub fn len(&self) -> usize {
        self.hot.len()
    }

    pub fn is_empty(&self) -> bool {
        self.hot.is_empty()
    }

    pub fn get(&self, i: usize) -> Particle {
        let (h, c) = (self.hot[i], self.cold[i]);
        Particle { id: c.id, pos: h.pos, vel: h.vel, mass: h.mass, charge: c.charge, radius: c.radius, temperature: c.temperature, species: c.species, flags: c.flags, tag: c.tag }
    }

    pub fn step(&mut self, dt: f32) {
        for p in &mut self.hot {
            p.vel[2] -= G * dt;
            p.pos[0] += p.vel[0] * dt;
            p.pos[1] += p.vel[1] * dt;
            p.pos[2] += p.vel[2] * dt;
        }
    }

    pub fn count_below(&self, ground: f32) -> usize {
        self.hot.iter().filter(|p| p.pos[2] < ground).count()
    }

    pub fn kinetic_energy(&self) -> f64 {
        self.hot.iter().map(|p| 0.5 * p.mass as f64 * p.vel.iter().map(|&v| v as f64 * v as f64).sum::<f64>()).sum()
    }
}
