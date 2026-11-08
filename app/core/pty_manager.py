import sys

if sys.platform.startswith("linux"):
    from app.systems.linux import PTYManager
else:
    raise NotImplementedError(
        f"PTYManager is not implemented for {sys.platform}"
    )