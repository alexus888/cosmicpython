from invoke import task


@task
def tests(c):
    c.run("poetry run pytest", pty=True)
