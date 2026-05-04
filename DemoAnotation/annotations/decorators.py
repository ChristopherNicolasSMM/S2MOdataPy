"""
Decorators declarativos de anotações de UI para modelos OData.

Inspirados no padrão de anotações do protocolo OData V4 com extensões de UI,
esses decorators permitem definir a apresentação de entidades diretamente
nas classes de modelo, de forma legível e sem dependência de arquivos externos.

Uso:
    @Common.Label("Clientes")
    @UI.ListView(columns=[UI.Field("CustomerID", label="Código")])
    @UI.FieldGroup("BasicInfo", label="Dados", fields=["CustomerID", "CompanyName"])
    @Validation.Required("CustomerID")
    class Customer(Base):
        ...

Author: Christopher N. S. M. Mauricio
"""

from typing import Dict, List, Optional


class UI:
    """Decorators para configuração de interface de usuário."""

    @staticmethod
    def Field(
        name: str,
        label: str = None,
        width: str = None,
        sortable: bool = False,
        filterable: bool = False,
    ) -> dict:
        """
        Define as propriedades de apresentação de um campo.

        Args:
            name (str): Nome do campo (deve coincidir com o atributo do modelo).
            label (str): Rótulo exibido na interface.
            width (str): Largura sugerida (ex: '100px', '15%').
            sortable (bool): Indica se a coluna pode ser ordenada.
            filterable (bool): Indica se o campo pode ser usado em filtros.

        Returns:
            dict: Dicionário de configuração do campo.
        """
        return {
            "name": name,
            "label": label or name,
            "width": width,
            "sortable": sortable,
            "filterable": filterable,
        }

    @classmethod
    def ListView(cls, columns: List[Dict], default_sort: str = None):
        """
        Configura a apresentação em modo lista/tabela.

        Args:
            columns (list): Lista de dicionários criados com UI.Field().
            default_sort (str): Ordenação padrão no formato 'campo dir'
                                (ex: 'CompanyName asc').

        Exemplo:
            @UI.ListView(
                columns=[
                    UI.Field("Name", label="Nome", sortable=True),
                    UI.Field("Country", label="País", filterable=True),
                ],
                default_sort="Name asc"
            )
        """

        def decorator(cls_entity):
            if not hasattr(cls_entity, "_ui_annotations"):
                cls_entity._ui_annotations = {}
            cls_entity._ui_annotations["ListView"] = {
                "columns": columns,
                "default_sort": default_sort,
            }
            return cls_entity

        return decorator

    @classmethod
    def FieldGroup(
        cls,
        name: str,
        label: str,
        fields: List[str],
        collapsible: bool = False,
    ):
        """
        Define um grupo de campos para exibição em formulário.

        Múltiplos FieldGroups podem ser aplicados à mesma entidade,
        cada um gerando uma seção separada no formulário.

        Args:
            name (str): Identificador único do grupo.
            label (str): Título exibido na seção.
            fields (list[str]): Lista de nomes de campos pertencentes ao grupo.
            collapsible (bool): Se True, o grupo pode ser recolhido na UI.

        Exemplo:
            @UI.FieldGroup("Address", label="Endereço",
                           fields=["Country", "City", "PostalCode"])
        """

        def decorator(cls_entity):
            if not hasattr(cls_entity, "_ui_annotations"):
                cls_entity._ui_annotations = {}
            if "FieldGroups" not in cls_entity._ui_annotations:
                cls_entity._ui_annotations["FieldGroups"] = []
            cls_entity._ui_annotations["FieldGroups"].append(
                {
                    "name": name,
                    "label": label,
                    "fields": fields,
                    "collapsible": collapsible,
                }
            )
            return cls_entity

        return decorator


class Common:
    """Decorators para metadados comuns de entidades."""

    @staticmethod
    def Label(value: str):
        """
        Define o rótulo legível da entidade.

        Args:
            value (str): Nome de exibição da entidade (ex: 'Clientes').

        Exemplo:
            @Common.Label("Clientes")
            class Customer(Base): ...
        """

        def decorator(cls_entity):
            if not hasattr(cls_entity, "_ui_annotations"):
                cls_entity._ui_annotations = {}
            cls_entity._ui_annotations["Label"] = value
            return cls_entity

        return decorator


class Validation:
    """
    Decorators para regras de validação declarativas.

    As validações são armazenadas como metadados na classe e expostas
    pelo endpoint /$metadata.json para consumo pelo cliente S2MOdataPy
    e por componentes de UI.

    Não executam validação em runtime no servidor — para isso use
    as restrições do SQLAlchemy (nullable, etc.) e/ou Pydantic.
    """

    @staticmethod
    def Required(field: str, message: str = "Campo obrigatório"):
        """
        Marca um campo como obrigatório.

        Args:
            field (str): Nome do campo.
            message (str): Mensagem de erro exibida quando vazio.
        """

        def decorator(cls_entity):
            if not hasattr(cls_entity, "_validations"):
                cls_entity._validations = {}
            cls_entity._validations.setdefault(field, []).append(
                {
                    "type": "required",
                    "message": message,
                }
            )
            return cls_entity

        return decorator

    @staticmethod
    def MaxLength(field: str, max_len: int, message: str = None):
        """
        Limita o comprimento máximo de um campo de texto.

        Args:
            field (str): Nome do campo.
            max_len (int): Número máximo de caracteres permitidos.
            message (str): Mensagem personalizada (opcional).
        """
        msg = message or f"Máximo de {max_len} caracteres"

        def decorator(cls_entity):
            if not hasattr(cls_entity, "_validations"):
                cls_entity._validations = {}
            cls_entity._validations.setdefault(field, []).append(
                {
                    "type": "max_length",
                    "max": max_len,
                    "message": msg,
                }
            )
            return cls_entity

        return decorator

    @staticmethod
    def MinLength(field: str, min_len: int, message: str = None):
        """
        Define o comprimento mínimo aceito para um campo de texto.

        Args:
            field (str): Nome do campo.
            min_len (int): Número mínimo de caracteres.
            message (str): Mensagem personalizada (opcional).
        """
        msg = message or f"Mínimo de {min_len} caracteres"

        def decorator(cls_entity):
            if not hasattr(cls_entity, "_validations"):
                cls_entity._validations = {}
            cls_entity._validations.setdefault(field, []).append(
                {
                    "type": "min_length",
                    "min": min_len,
                    "message": msg,
                }
            )
            return cls_entity

        return decorator

    @staticmethod
    def Pattern(field: str, regex: str, message: str = "Formato inválido"):
        """
        Valida o campo contra uma expressão regular.

        Args:
            field (str): Nome do campo.
            regex (str): Expressão regular a validar.
            message (str): Mensagem de erro quando inválido.
        """

        def decorator(cls_entity):
            if not hasattr(cls_entity, "_validations"):
                cls_entity._validations = {}
            cls_entity._validations.setdefault(field, []).append(
                {
                    "type": "pattern",
                    "regex": regex,
                    "message": message,
                }
            )
            return cls_entity

        return decorator

    @staticmethod
    def Email(field: str, message: str = "E-mail inválido"):
        """
        Valida o campo como endereço de e-mail.

        Atalho para Validation.Pattern com regex de e-mail.
        """
        return Validation.Pattern(
            field,
            r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$",
            message,
        )
