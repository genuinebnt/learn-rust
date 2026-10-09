def C(id, module, slug, tier, title, diff, tests, learn, concepts, what, why, contract, invariants, relations, examples, checks, src=None, test=None):
    d = dict(id=id, module=module, slug=slug, tier=tier, title=title, diff=diff, tests=tests, learn=learn, concepts=concepts, what=what, why=why,
             contract=contract, invariants=invariants, relations=relations, examples=examples, checks=checks)
    if src:
        d["src"] = dict(path=src[0], code=src[1])
    if test:
        d["test"] = dict(file=test[0], code=test[1])
    return d
