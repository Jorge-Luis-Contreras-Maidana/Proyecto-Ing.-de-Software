from contextlib import contextmanager

from app.extensions import db


@contextmanager
def unit_of_work():
    """Agrupa varias operaciones en una sola transacción: todo se guarda o nada. RNF-04."""
    try:
        yield db.session
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
