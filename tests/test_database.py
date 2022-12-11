# docker run --rm -P -p 127.0.0.1:5432:5432 --name postgres_mlops -e POSTGRES_PASSWORD=v45wbge8rl -d postgres

from sqlalchemy import create_engine

def test_db_connection():
    engine = create_engine('postgresql://postgres:v45wbge8rl@localhost:5432/postgres')
    
    with engine.begin() as conn:
        result = conn.execute('SELECT schema_name FROM information_schema.schemata').all()
        result = [item for subresult in result for item in subresult ]
        
    assert 'public' in result
