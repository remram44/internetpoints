from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

from internetpoints import config, models


# Setup SQLAlchemy
engine = create_engine(config.DATABASE_URI)
Session = sessionmaker(bind=engine)
if not engine.dialect.has_table(engine.connect(), 'threads'):
    models.Base.metadata.create_all(bind=engine)
