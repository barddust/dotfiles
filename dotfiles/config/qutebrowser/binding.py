import yaml

c.bindings.default = {}

with (config.configdir / 'binding.yaml').open() as f:
    BINDINGS = yaml.safe_load(f)
    
for m, each in BINDINGS.items():
    for k, c in each.items():
        config.bind(k, c, mode=m)
