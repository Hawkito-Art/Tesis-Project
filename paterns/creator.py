"""Ejemplo de patrón Creator (Factory) para construir entidades.

工厂: normaliza datos crudos (filas de planilla importada) y crea
instancias de modelos Django listas para persistir.

En producción vive en: tesis/apps/<app>/factories.py
"""
from typing import Dict, Any
from decimal import Decimal
import logging

from .models import Entity, Indicator, IndicatorRecord, Period

logger = logging.getLogger(__name__)


class EntityCreator:

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> Entity:
        
        codigo = raw.get("codigo") or raw.get("code") or raw.get("entity_code")
        nombre = raw.get("nombre") or raw.get("name") or raw.get("entity_name")

        if not nombre:
            raise ValueError("El campo 'nombre' es obligatorio")

        entity = Entity(
            code=codigo or "",
            name=nombre.strip(),
            entity_type=raw.get("tipo_entidad") or raw.get("entity_type") or "otro",
            is_active=True,
        )
        return entity

    @classmethod
    def create_batch(cls, rows: list[Dict[str, Any]]) -> list[Entity]:
        """Crea múltiples instancias Entity en batch.

        Args:
            rows: lista de dicts crudos.
        Returns:
            Lista de Entity instances (sin guardar).
        """
        entities = []
        for row in rows:
            try:
                entities.append(cls.from_dict(row))
            except ValueError as e:
                logger.warning(f"Fila ignorada: {e}")
                continue
        return entities


class IndicatorFactory:

    def __init__(self, default_unit: str = "U", default_group_id: int | None = None):
        self.default_unit = default_unit
        self.default_group_id = default_group_id

    def from_dict(self, raw: Dict[str, Any]) -> Indicator:
        
        code = raw.get("codigo") or raw.get("code") or raw.get("indicator_code")
        name = raw.get("nombre") or raw.get("name") or raw.get("indicator_name")
        unit = raw.get("unidad") or raw.get("unit") or self.default_unit
        category = raw.get("categoria") or raw.get("category") or "general"

        if not name:
            raise ValueError("El campo 'nombre' del indicador es obligatorio")

        indicator = Indicator(
            code=code or "",
            name=name.strip(),
            unit=unit,
            category=category.strip().lower(),
            group_id=self.default_group_id,
            is_active=True,
        )
        return indicator

    def from_code(self, code: str) -> Indicator:
        """Busca o crea un Indicator por código (get-or-create)."""
        indicator, created = Indicator.objects.get_or_create(
            code=code,
            defaults={"name": code, "unit": self.default_unit, "is_active": True},
        )
        return indicator


class IndicatorRecordFactory:
    """Factory para construir IndicatorRecord vinculando entity, indicator y period."""

    def __init__(self):
        self.indicator_factory = IndicatorFactory()
        self.errors: list[str] = []

    def from_dict(self, raw: Dict[str, Any]) -> IndicatorRecord | None:
        """Construye un IndicatorRecord desde dict crudo.

        Args:
            raw: dict esperado con 'entity_id', 'indicator_id'/'indicator_code',
                 'period_id'/'period', 'variable_name', 'value'.
        Returns:
            IndicatorRecord instance o None si no se puede vincular.
        """
        entity_id = raw.get("entity_id")
        indicator_ref = raw.get("indicator_id") or raw.get("indicator_code")
        period_ref = raw.get("period_id") or raw.get("period")
        variable = raw.get("variable_name") or raw.get("variable") or "valor"
        value_raw = raw.get("value") or raw.get("valor") or 0

        try:
            value = Decimal(str(value_raw).replace(",", "."))
        except Exception:
            self.errors.append(f"Value inválido: {value_raw}")
            value = Decimal("0")

        entity = None
        if entity_id:
            try:
                entity = Entity.objects.get(pk=entity_id, is_active=True)
            except Entity.DoesNotExist:
                self.errors.append(f"Entity {entity_id} no existe")
                return None

        indicator = None
        if indicator_ref:
            if isinstance(indicator_ref, int):
                try:
                    indicator = Indicator.objects.get(pk=indicator_ref, is_active=True)
                except Indicator.DoesNotExist:
                    self.errors.append(f"Indicator {indicator_ref} no existe")
            else:
                indicator = self.indicator_factory.from_code(str(indicator_ref))

        period = None
        if period_ref:
            try:
                if isinstance(period_ref, int):
                    period = Period.objects.get(pk=period_ref)
                else:
                    period = Period.objects.get(year=int(period_ref))
            except Period.DoesNotExist:
                self.errors.append(f"Period '{period_ref}' no existe")

        if not entity or not indicator:
            return None

        record = IndicatorRecord(
            indicator=indicator,
            entity=entity,
            period=period,
            variable_name=variable.strip(),
            value=value,
            is_active=True,
        )
        return record

    def create_batch(self, rows: list[Dict[str, Any]], save: bool = True) -> list[IndicatorRecord]:
        """Procesa múltiples filas y crea IndicatorRecords en batch.

        Args:
            rows: lista de dicts crudos.
            save: si True, persiste cada instancia en BD.
        Returns:
            Lista de IndicatorRecord (creadas o ya existentes).
        """
        created = []
        for row in rows:
            record = self.from_dict(row)
            if record is None:
                continue
            if save:
                record.save()
            created.append(record)
        return created


def import_from_spreadsheet(rows: list[Dict[str, Any]]) -> Dict[str, Any]:
    """Helper de alto nivel: importa filas de planilla a BD.

    1. Crea/recupera Entities por código.
    2. Crea/recupera Indicators por código.
    3. Crea IndicatorRecords vinculando todo.
    4. Retorna estadísticas del proceso.
    """
    entity_factory = EntityFactory()
    record_factory = IndicatorRecordFactory()

    entities = entity_factory.create_batch(rows)
    for entity in entities:
        entity, created = Entity.objects.get_or_create(
            code=entity.code,
            defaults={"name": entity.name, "entity_type": entity.entity_type},
        )

    records = record_factory.create_batch(rows, save=True)

    return {
        "entities_created": len([e for e in entities if e.pk is None]),
        "records_created": len(records),
        "errors": record_factory.errors,
    }


if __name__ == "__main__":
    factory = IndicatorFactory(default_unit="CUP")
    sample = {"codigo": "IND001", "nombre": "Ingreso per cápita", "unidad": "CUP", "categoria": "economico"}
    ind = factory.from_dict(sample)
    print(f"Indicator preparado: {ind.name}, unidad={ind.unit}")
