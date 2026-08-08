from app.database.database import Base, engine
from app.database import models

Base.metadata.create_all(bind=engine)

print("✅ Database created")