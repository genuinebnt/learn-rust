`expire` doesn't compile: it removes entries from the map it's iterating and edits other entries on the
way. Fix it without cloning any session. The result must not depend on the map's iteration order.
