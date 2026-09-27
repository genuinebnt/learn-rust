`group_runs` doesn't compile: values are moved inside the loop and then used again, in the same
iteration or the next one. Fix it without cloning and without building any `Vec` twice.
