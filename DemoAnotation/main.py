"""
Servidor OData V4 com anotações de UI.

Demonstra a integração de:
- FastAPI como servidor HTTP
- SQLAlchemy como ORM (SQLite em dev, PostgreSQL em prod)
- Anotações de UI declarativas via decorators Python
- Geração automática de $metadata em XML e JSON

Uso:
    uvicorn main:app --reload --port 8000

Endpoints principais:
    GET /                          — health check
    GET /odata/$metadata           — metadados OData V4 em XML
    GET /odata/$metadata.json      — metadados enriquecidos em JSON (para S2MOdataPy)
    GET /odata/{entity}            — listar registros
    GET /odata/{entity}({key})     — buscar por chave
    POST   /odata/{entity}         — criar registro
    PUT    /odata/{entity}({key})  — substituir registro
    PATCH  /odata/{entity}({key})  — atualizar parcialmente
    DELETE /odata/{entity}({key})  — remover registro

Author: Christopher N. S. M. Mauricio
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import Response

load_dotenv()
ENV = os.getenv("ENVIRONMENT", "dev")

from annotations.metadata_builder import build_metadata_dict, build_metadata_xml

# Importa modelos ANTES de criar tabelas (necessário para o SQLAlchemy registrá-los)
from database import Base, engine, get_db
from models.customer import Customer  # noqa: F401
from models.order import Order  # noqa: F401
from models.product import Product  # noqa: F401
from odata.endpoint import ENTITY_MAP
from odata.endpoint import router as odata_router

# ─────────────────────────────────────────────────────────────────────────────
# Startup
# ─────────────────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialização e encerramento da aplicação."""
    print("[Server] Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("[Server] Tabelas prontas.")

    if ENV == "dev":
        print("[Server] Ambiente DEV — verificando dados mock...")
        db = next(get_db())
        try:
            if db.query(Customer).count() == 0:
                print("[Server] Banco vazio. Carregando dados mock...")
                from mock_data import load_mock_data

                load_mock_data(db)
            else:
                print("[Server] Banco já populado. Nenhuma ação necessária.")
        except Exception as e:
            print(f"[Server] Aviso ao verificar dados: {e}")
        finally:
            db.close()

    print(f"[Server] Pronto! Ambiente: {ENV.upper()}")
    yield
    print("[Server] Encerrando.")


# ─────────────────────────────────────────────────────────────────────────────
# Aplicação
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="S2MOdataPy Demo Server",
    description=(
        "Servidor OData V4 com anotações de UI declarativas. "
        "Utilize os endpoints /odata/$metadata e /odata/$metadata.json "
        "para explorar a estrutura das entidades disponíveis."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ─────────────────────────────────────────────────────────────────────────────
# Metadata endpoints
# Definidos em main.py (fora do router /odata) para evitar conflito de rota
# com o parâmetro {entity} definido no endpoint.py.
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/odata/$metadata", include_in_schema=False)
def metadata_xml():
    """
    Retorna os metadados do serviço em XML padrão OData V4.

    Inclui definição de EntityType, anotações de ListView (UI.LineItem)
    e FieldGroups (UI.FieldGroup) para cada entidade registrada.
    """
    entities = list(ENTITY_MAP.values())
    xml_content = build_metadata_xml(entities)
    return Response(content=xml_content, media_type="application/xml; charset=utf-8")


@app.get("/odata/$metadata.json")
def metadata_json():
    """
    Retorna os metadados em formato JSON enriquecido.

    Formato customizado (não padrão OData) consumido pelo cliente S2MOdataPy.
    Inclui propriedades, anotações de UI e regras de validação por entidade.
    """
    entities = list(ENTITY_MAP.values())
    return build_metadata_dict(entities)


# ─────────────────────────────────────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────────────────────────────────────

app.include_router(odata_router)


# ─────────────────────────────────────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "S2MOdataPy Demo Server",
        "version": "1.0.0",
        "entities": list(ENTITY_MAP.keys()),
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "metadata": "/odata/$metadata",
            "meta_json": "/odata/$metadata.json",
        },
    }
