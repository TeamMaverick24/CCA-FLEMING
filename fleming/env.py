
import environ
import os
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
env.read_env(
    env.path(
        'FILE',
        default=(environ.Path(__file__) - 2).path("flemingenv/.env")()
)())
