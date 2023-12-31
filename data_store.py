from sqlalchemy import Column, Integer, MetaData, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import db_url_object

metadata = MetaData()
Base = declarative_base(metadata=metadata)
engine = create_engine(db_url_object)
metadata.create_all(engine)

class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = Column(Integer, primary_key=True)
    worksheet_id = Column(Integer, primary_key=True)

def add_user(profile_id, worksheet_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        new_record = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
        session.add(new_record)
        session.commit()
        return True
    except:
        session.rollback()
        return False
    finally:
        session.close()

def check_user(profile_id, worksheet_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        record = session.query(Viewed).filter_by(profile_id=profile_id, worksheet_id=worksheet_id).first()
        if record:
            return True
        else:
            return False
    except:
        return False
    finally:
        session.close()

if __name__ == '__main__':
    # Пример использования функций внутри файла data_store.py
    profile_id = 9999
    worksheet_id = 000000
    add_user(profile_id, worksheet_id)
    res = check_user(profile_id, worksheet_id)
    print(res)
