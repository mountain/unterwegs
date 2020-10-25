import tasks as ts


@ts.app.task
def fire(t):
    return t

