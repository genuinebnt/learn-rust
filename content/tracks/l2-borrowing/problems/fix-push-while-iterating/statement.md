`expand` doesn't compile: it pushes to `tasks` while iterating over it. Here that's the point, since
added tasks must be expanded too. Fix it without a second collection of tasks.
