A particle simulation steps a million particles per frame. `Particles` stores them as a
`Vec<Particle>`, 88 bytes each, but the integrator reads and writes only `pos` and `vel` (24 bytes),
and the ground-contact check reads only `pos.z` (4 bytes). Every frame drags the rest of each
struct (ids, tags, thermodynamics) through the cache.

Store the particles as a **structure of arrays**, keeping the API: `push` and `get` still take and
return `Particle`, and `step`, `count_below` and `kinetic_energy` give the same results (`step` is
bit-for-bit the same arithmetic). The tests time your code against the array-of-structs loop, in a
release build:

- `step` on 262 144 particles must be at least **2.5×** faster;
- `count_below` on 1 048 576 particles must be at least **6×** faster.
