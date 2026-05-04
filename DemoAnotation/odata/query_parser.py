"""
Parser de parâmetros de query OData V4 para SQLAlchemy.

Processa os parâmetros de URL ($filter, $orderby, $top, $skip)
e aplica as operações correspondentes em queries SQLAlchemy.

Author: Christopher N. S. M. Mauricio
"""

import re

from sqlalchemy import asc, desc
from sqlalchemy.inspection import inspect as sa_inspect

# ─────────────────────────────────────────────────────────────────────────────
# Filtros ($filter)
# ─────────────────────────────────────────────────────────────────────────────

# Captura expressões com valor string entre aspas simples: campo op 'valor'
_PATTERN_STR = r"(\w+)\s+(eq|ne|gt|ge|lt|le|contains)\s+'([^']*)'"

# Captura expressões com valor numérico sem aspas: campo op 123.45
_PATTERN_NUM = r"(\w+)\s+(eq|ne|gt|ge|lt|le)\s+(-?\d+(?:\.\d+)?)"

# Captura contains(campo, 'valor')
_PATTERN_FUNC = r"contains\((\w+)\s*,\s*'([^']*)'\)"


def apply_odata_filters(query, model, filter_str: str = None):
    """
    Aplica a expressão $filter em uma query SQLAlchemy.

    Suporta:
    - Comparações com string:  Country eq 'Mexico'
    - Comparações numéricas:   UnitPrice gt 10.5
    - Função contains:         contains(CompanyName, 'Tech')
    - Operadores: eq, ne, gt, ge, lt, le, contains

    Args:
        query: Query SQLAlchemy ativa.
        model: Classe do modelo SQLAlchemy.
        filter_str (str): Expressão $filter da URL.

    Returns:
        Query SQLAlchemy com filtros aplicados.
    """
    if not filter_str:
        return query

    # --- contains(campo, 'valor') ---
    for field_name, value in re.findall(_PATTERN_FUNC, filter_str):
        column = getattr(model, field_name, None)
        if column is not None:
            query = query.filter(column.ilike(f"%{value}%"))

    # --- campo op 'valor' (string) ---
    for field_name, op, value in re.findall(_PATTERN_STR, filter_str):
        column = getattr(model, field_name, None)
        if column is None:
            continue
        query = _apply_op(query, column, op, value)

    # --- campo op número ---
    for field_name, op, value in re.findall(_PATTERN_NUM, filter_str):
        column = getattr(model, field_name, None)
        if column is None:
            continue
        # Converte para int ou float conforme necessário
        numeric = float(value) if "." in value else int(value)
        query = _apply_op(query, column, op, numeric)

    return query


def _apply_op(query, column, op: str, value):
    """Aplica um operador de comparação à coluna."""
    ops = {
        "eq": column == value,
        "ne": column != value,
        "gt": column > value,
        "ge": column >= value,
        "lt": column < value,
        "le": column <= value,
        "contains": column.ilike(f"%{value}%"),
    }
    condition = ops.get(op)
    if condition is not None:
        query = query.filter(condition)
    return query


# ─────────────────────────────────────────────────────────────────────────────
# Ordenação ($orderby)
# ─────────────────────────────────────────────────────────────────────────────


def apply_odata_orderby(query, model, orderby_str: str = None):
    """
    Aplica $orderby em uma query SQLAlchemy.

    Suporta múltiplos campos separados por vírgula.
    Direção padrão: asc. Quando omitido, ordena pela chave primária.

    Exemplos:
        CompanyName asc
        Country desc, CompanyName asc

    Args:
        query: Query SQLAlchemy ativa.
        model: Classe do modelo SQLAlchemy.
        orderby_str (str): Expressão $orderby da URL.

    Returns:
        Query SQLAlchemy com ordenação aplicada.
    """
    if not orderby_str:
        # Ordenação padrão pela chave primária
        pk_name = sa_inspect(model).primary_key[0].name
        return query.order_by(asc(getattr(model, pk_name)))

    for part in orderby_str.split(","):
        part = part.strip()
        if part.endswith(" desc"):
            col_name = part[:-5].strip()
            col = getattr(model, col_name, None)
            if col is not None:
                query = query.order_by(desc(col))
        else:
            col_name = part.replace(" asc", "").strip()
            col = getattr(model, col_name, None)
            if col is not None:
                query = query.order_by(asc(col))

    return query


# ─────────────────────────────────────────────────────────────────────────────
# Paginação ($top / $skip)
# ─────────────────────────────────────────────────────────────────────────────


def apply_odata_pagination(query, top: int = None, skip: int = None, default_top: int = 20):
    """
    Aplica $top e $skip em uma query SQLAlchemy.

    Args:
        query: Query SQLAlchemy ativa.
        top (int): Máximo de registros a retornar.
        skip (int): Registros a pular (offset).
        default_top (int): Valor padrão de limite quando $top não é informado.

    Returns:
        Query SQLAlchemy paginada.
    """
    if skip is not None and skip > 0:
        query = query.offset(skip)
    limit = top if top is not None else default_top
    return query.limit(limit)
