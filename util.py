def build_opts(opts):
    return {key: value for (key, value) in map(lambda x: x.split("="), opts)}
