def enter_if_accessible(function=None, *args, **kwargs):
    if function:
        return function
    return lambda f: f
