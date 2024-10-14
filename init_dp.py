from sql.database import Base, engine
from sql.models import User


Base.metadata.create_all(bind=engine)