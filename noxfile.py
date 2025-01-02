import nox


@nox.session(venv_backend="uv")
@nox.parametrize('python', ("3.10", "3.11", "3.12", "3.13"))
def test(session: nox.Session, python: str) -> None:
    """
    Run the unit tests.
    """
    session.run_install(
        "uv",
        "sync",
        "--python",
        python,
        "--python-preference",
        "only-managed",
        "--extra=test",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("pytest", *session.posargs)
