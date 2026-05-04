"""
Router OData V4 — endpoints de entidades (leitura e escrita).

FastAPI/Starlette não suporta parênteses literais em parâmetros de rota
(ex: /{entity}({key})). A solução adotada é capturar o segmento completo
como {entity_segment} e separar entity / key em Python, detectando a
presença de '(' na string.

Rotas expostas:
  GET    /odata/{segment}           — lista OU busca por chave
  POST   /odata/{entity}            — criar registro
  PUT    /odata/{segment_com_chave} — substituir registro
  PATCH  /odata/{segment_com_chave} — atualizar parcialmente
  DELETE /odata/{segment_com_chave} — remover registro

Author: Christopher N. S. M. Mauricio
"""

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from models.customer import Customer
from models.order import Order
from models.product import Product
from odata.query_parser import (
    apply_odata_filters,
    apply_odata_orderby,
    apply_odata_pagination,
)
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import Session

router = APIRouter(prefix="/odata", tags=["OData"])

ENTITY_MAP: dict = {
    "Customers": Customer,
    "Orders": Order,
    "Products": Product,
}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _row_to_dict(row) -> dict:
    d = row.__dict__.copy()
    d.pop("_sa_instance_state", None)
    return d


def _get_pk_name(model) -> str:
    return sa_inspect(model).primary_key[0].name


def _parse_key(key_str: str):
    if key_str.startswith("'") and key_str.endswith("'"):
        return key_str[1:-1]
    try:
        return int(key_str)
    except ValueError:
        return key_str


def _get_entity_or_404(entity: str):
    model = ENTITY_MAP.get(entity)
    if model is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entidade '{entity}' não encontrada. Disponíveis: {list(ENTITY_MAP.keys())}",
        )
    return model


def _split_entity_key(segment: str):
    """
    'Customers(\'ALFKI\')' -> ('Customers', "'ALFKI'")
    'Orders(1)'            -> ('Orders', '1')
    'Customers'            -> ('Customers', None)
    """
    if "(" in segment and segment.endswith(")"):
        entity_name, rest = segment.split("(", 1)
        return entity_name.strip(), rest.rstrip(")").strip()
    return segment.strip(), None


# ─────────────────────────────────────────────────────────────────────────────
# GET — lista OU busca por chave
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/{entity_segment}")
def odata_get(
    entity_segment: str,
    request: Request,
    filter_param: str = Query(None, alias="$filter"),
    orderby_param: str = Query(None, alias="$orderby"),
    top_param: int = Query(None, alias="$top", ge=0),
    skip_param: int = Query(None, alias="$skip", ge=0),
    select_param: str = Query(None, alias="$select"),
    count_param: str = Query(None, alias="$count"),
    db: Session = Depends(get_db),
):
    """GET unificado: sem chave → lista; com chave → busca individual."""
    entity_name, key_raw = _split_entity_key(entity_segment)

    if key_raw is not None:
        model = _get_entity_or_404(entity_name)
        pk_name = _get_pk_name(model)
        pk_value = _parse_key(key_raw)
        row = db.query(model).filter(getattr(model, pk_name) == pk_value).first()
        if row is None:
            raise HTTPException(
                status_code=404, detail=f"Registro '{key_raw}' não encontrado em '{entity_name}'"
            )
        return _row_to_dict(row)

    model = _get_entity_or_404(entity_name)
    query = db.query(model)
    query = apply_odata_filters(query, model, filter_param)
    total_count = query.count()
    query = apply_odata_orderby(query, model, orderby_param)
    query = apply_odata_pagination(query, top_param, skip_param)
    data = [_row_to_dict(r) for r in query.all()]

    if select_param:
        fields = [f.strip() for f in select_param.split(",")]
        data = [{f: item.get(f) for f in fields if f in item} for item in data]

    response = {
        "@odata.context": f"{request.base_url}odata/$metadata#{entity_name}",
        "value": data,
    }
    if count_param and count_param.lower() == "true":
        response["@odata.count"] = total_count
    return response


# ─────────────────────────────────────────────────────────────────────────────
# POST — criar
# ─────────────────────────────────────────────────────────────────────────────


@router.post("/{entity}", status_code=201)
async def odata_create(entity: str, request: Request, db: Session = Depends(get_db)):
    """Cria um novo registro. Body: JSON com campos do registro."""
    model = _get_entity_or_404(entity)
    data = await request.json()
    valid_cols = {c.name for c in sa_inspect(model).columns}
    instance = model(**{k: v for k, v in data.items() if k in valid_cols})
    db.add(instance)
    try:
        db.commit()
        db.refresh(instance)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar: {e}")
    return _row_to_dict(instance)


# ─────────────────────────────────────────────────────────────────────────────
# PUT — substituir completamente
# ─────────────────────────────────────────────────────────────────────────────


@router.put("/{entity_segment}", status_code=200)
async def odata_update(entity_segment: str, request: Request, db: Session = Depends(get_db)):
    """Substitui completamente um registro (PUT). URL: /entity(key)"""
    entity_name, key_raw = _split_entity_key(entity_segment)
    if key_raw is None:
        raise HTTPException(status_code=400, detail="PUT requer chave na URL")
    model = _get_entity_or_404(entity_name)
    pk_name = _get_pk_name(model)
    pk_value = _parse_key(key_raw)
    row = db.query(model).filter(getattr(model, pk_name) == pk_value).first()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Registro '{key_raw}' não encontrado")
    data = await request.json()
    valid_cols = {c.name for c in sa_inspect(model).columns}
    for k, v in data.items():
        if k in valid_cols and k != pk_name:
            setattr(row, k, v)
    try:
        db.commit()
        db.refresh(row)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar: {e}")
    return _row_to_dict(row)


# ─────────────────────────────────────────────────────────────────────────────
# PATCH — atualizar parcialmente
# ─────────────────────────────────────────────────────────────────────────────


@router.patch("/{entity_segment}", status_code=200)
async def odata_patch(entity_segment: str, request: Request, db: Session = Depends(get_db)):
    """Atualiza parcialmente um registro (PATCH). URL: /entity(key)"""
    entity_name, key_raw = _split_entity_key(entity_segment)
    if key_raw is None:
        raise HTTPException(status_code=400, detail="PATCH requer chave na URL")
    model = _get_entity_or_404(entity_name)
    pk_name = _get_pk_name(model)
    pk_value = _parse_key(key_raw)
    row = db.query(model).filter(getattr(model, pk_name) == pk_value).first()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Registro '{key_raw}' não encontrado")
    data = await request.json()
    valid_cols = {c.name for c in sa_inspect(model).columns}
    for k, v in data.items():
        if k in valid_cols and k != pk_name:
            setattr(row, k, v)
    try:
        db.commit()
        db.refresh(row)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar: {e}")
    return _row_to_dict(row)


# ─────────────────────────────────────────────────────────────────────────────
# DELETE — remover
# ─────────────────────────────────────────────────────────────────────────────


@router.delete("/{entity_segment}", status_code=204)
def odata_delete(entity_segment: str, db: Session = Depends(get_db)):
    """Remove um registro. URL: /entity(key). Retorna 204 em sucesso."""
    entity_name, key_raw = _split_entity_key(entity_segment)
    if key_raw is None:
        raise HTTPException(status_code=400, detail="DELETE requer chave na URL")
    model = _get_entity_or_404(entity_name)
    pk_name = _get_pk_name(model)
    pk_value = _parse_key(key_raw)
    row = db.query(model).filter(getattr(model, pk_name) == pk_value).first()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Registro '{key_raw}' não encontrado")
    try:
        db.delete(row)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao remover: {e}")
    return Response(status_code=204)
