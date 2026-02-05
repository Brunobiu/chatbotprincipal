from app.db.base import Base
from app.db.session import engine

def main():
    print('Criando tabelas no banco de dados...')
    Base.metadata.create_all(bind=engine)
    print('Tabelas criadas.')

if __name__ == '__main__':
    main()

