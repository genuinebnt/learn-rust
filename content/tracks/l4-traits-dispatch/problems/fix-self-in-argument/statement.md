`winner` doesn't compile: `Player` is not dyn-compatible, for two different reasons. Fix the trait so that
`winner` works and players of different types can be compared (`human.beats(&team)`). Keep `new`.
