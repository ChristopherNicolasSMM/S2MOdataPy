"""
Configuração dos testes — pytest fixtures compartilhadas.

Os testes utilizam a biblioteca S2MOdataPy para consumir o servidor OData.
Para rodar:

    # 1. Instale as dependências do servidor
    pip install -r ../requirements.txt

    # 2. Instale a biblioteca S2MOdataPy (pasta irmã do DemoAnotation)
    pip install -e ../../S2MOdataPy

    # 3. Execute os testes
    cd tests
    pytest -v

    # OU a partir da raiz do DemoAnotation
    pytest tests/ -v

Author: Christopher N. S. M. Mauricio
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Garante que o diretório raiz do DemoAnotation está no path do Python
# (necessário para os imports absolutos: from database import ..., etc.)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Tenta localizar S2MOdataPy como pacote instalado; caso não esteja,
# adiciona o diretório irmão ao path automaticamente.
try:
    import s2modatapy  # noqa: F401
except ImportError:
    sibling = os.path.join(ROOT, "..", "S2MOdataPy")
    sibling = os.path.normpath(sibling)
    if os.path.isdir(sibling):
        sys.path.insert(0, sibling)
        print(f"[conftest] S2MOdataPy carregado de: {sibling}")
    else:
        raise ImportError(
            "S2MOdataPy não encontrado. Instale com: pip install -e ../../S2MOdataPy\n"
            f"  (buscado em: {sibling})"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Configuração de banco em memória para testes
# ─────────────────────────────────────────────────────────────────────────────

os.environ["ENVIRONMENT"] = "test"
os.environ["SQLITE_DB"]   = ":memory:"

# ─────────────────────────────────────────────────────────────────────────────
# Configura um engine SQLite em memória com StaticPool para que TODAS as
# conexões/sessões durante os testes compartilhem o mesmo banco.
# Sem StaticPool, cada nova conexão recebe um banco vazio — os dados
# inseridos por um fixture desaparecem na próxima sessão.
# ─────────────────────────────────────────────────────────────────────────────
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)
_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

# Importa Base e models para que o SQLAlchemy registre todos os metadados
from database import Base, get_db  # noqa: E402
from models.customer import Customer  # noqa: F401, E402
from models.order    import Order     # noqa: F401, E402
from models.product  import Product   # noqa: F401, E402

# Cria as tabelas UMA VEZ no engine compartilhado
Base.metadata.create_all(bind=_test_engine)

# Popula dados mock UMA VEZ
_seed_done = False
_seed_db = _TestSessionLocal()
try:
    from mock_data import load_mock_data
    load_mock_data(_seed_db)
    _seed_done = True
except Exception as e:
    print(f"[conftest] Aviso ao carregar mock data: {e}")
finally:
    _seed_db.close()


def _override_get_db():
    """Dependency override — usa o engine compartilhado com StaticPool."""
    db = _TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def test_app():
    """
    Instância da aplicação FastAPI configurada para testes.

    Usa banco SQLite em memória com StaticPool — completamente isolado
    da base de desenvolvimento e compartilhado entre todos os testes.
    """
    from main import app
    app.dependency_overrides[get_db] = _override_get_db
    return app


@pytest.fixture(scope="session")
def http_client(test_app):
    """
    TestClient do FastAPI — simula requisições HTTP sem servidor real.

    Todos os testes de endpoint usam este client.
    """
    with TestClient(test_app) as client:
        yield client


@pytest.fixture(scope="session")
def odata_client(http_client):
    """
    Cliente S2MOdataPy configurado para usar o TestClient interno.

    Utiliza um transport customizado que roteia as requisições para o
    FastAPI TestClient, sem necessidade de servidor HTTP real.
    """
    from s2modatapy import S2MClient

    class TestTransport:
        """Adapter que roteia S2MOdataPy → FastAPI TestClient."""

        def __init__(self, tc):
            self._tc = tc

        def get(self, url, **kwargs):
            return self._tc.get(url, **kwargs)

        def post(self, url, **kwargs):
            return self._tc.post(url, **kwargs)

        def put(self, url, **kwargs):
            return self._tc.put(url, **kwargs)

        def patch(self, url, **kwargs):
            return self._tc.patch(url, **kwargs)

        def delete(self, url, **kwargs):
            return self._tc.delete(url, **kwargs)

    client = S2MClient("http://testserver/odata/", debug=False)
    # Substitui a sessão HTTP pelo TestClient
    client.session = http_client
    return client
