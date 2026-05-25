"""Ejemplo de patrón Experto en Información (Service / Selector).

Encapsula reglas de negocio, agregaciones y validaciones relacionadas
con indicadores económicos municipales.

En producción vive en: tesis/apps/<app>/services.py / selectors.py
"""
from typing import Dict, Any
from decimal import Decimal
from django.db.models import Sum, Avg, Count, Q, F, Value, FloatField
from django.db.models.functions import Coalesce

from .models import Entity, Indicator, IndicatorRecord, Period


class IndicatorCheck:
    def compute_accumulated(self, rows: list[Dict[str, Any]]) -> Dict[str, Any]:
        
        accum: Dict[str, Decimal] = {}
        for r in rows:
            cat = r.get("category") or "sin_categoria"
            val = r.get("value") or 0
            if isinstance(val, str):
                val = Decimal(val.replace(",", "."))
            accum[cat] = accum.get(cat, Decimal("0")) + Decimal(str(val))
        return accum

    def get_accumulated_by_entity(
        self, period: int, category: str | None = None
    ) -> Dict[str, Decimal]:
        
        filters = Q(indicator__is_active=True) & Q(is_active=True) & Q(period__year=period)
        if category:
            filters &= Q(indicator__category=category)

        records = (
            IndicatorRecord.objects
            .filter(filters)
            .values("entity__name")
            .annotate(total=Coalesce(Sum("value"), Value(0, output_field=FloatField())))
        )
        return {r["entity__name"]: r["total"] for r in records}

    def get_rolling_average(
        self, entity_id: int, indicator_code: str, years: int = 3
    ) -> Decimal | None:
        """Calcula promedio móvil de un indicador sobre los últimos N años.

        Args:
            entity_id: ID de la entidad.
            indicator_code: código del indicador.
            years: cantidad de años hacia atrás (incluyendo actual).
        Returns:
            Promedio Decimal o None si no hay datos.
        """
        try:
            indicator = Indicator.objects.get(code=indicator_code, is_active=True)
        except Indicator.DoesNotExist:
            return None

        records = (
            IndicatorRecord.objects
            .filter(
                entity_id=entity_id,
                indicator=indicator,
                is_active=True,
                period__is_active=True,
            )
            .order_by("-period__year")
            .values("value")[:years]
        )

        if not records:
            return None

        total = sum(Decimal(str(r["value"])) for r in records)
        return total / len(list(records))

    def compute_correlation(self, entity_id: int, period: int) -> Dict[str, Any]:
        """Estima correlación simple entre indicadores de una entidad.

        Calcula covarianza y correlación de Pearson simplificada
        entre pares de indicadores que comparten período.
        """
        records = (
            IndicatorRecord.objects
            .filter(
                entity_id=entity_id,
                period__year=period,
                is_active=True,
            )
            .select_related("indicator")
            .values("indicator__code", "indicator__name", "value")
        )

        data = {}
        for r in records:
            code = r["indicator__code"]
            if code not in data:
                data[code] = {"name": r["indicator__name"], "values": []}
            data[code]["values"].append(Decimal(str(r["value"])))

        if len(data) < 2:
            return {"error": "Se requieren al menos 2 indicadores"}

        codes = list(data.keys())
        x_vals = data[codes[0]]["values"]
        y_vals = data[codes[1]]["values"]

        n = min(len(x_vals), len(y_vals))
        if n == 0:
            return {"error": "Sin datos para correlacionar"}

        x_mean = sum(x_vals[:n]) / n
        y_mean = sum(y_vals[:n]) / n

        cov = sum((x_vals[i] - x_mean) * (y_vals[i] - y_mean) for i in range(n)) / n
        x_std = (sum((v - x_mean) ** 2 for v in x_vals[:n]) / n) ** 0.5
        y_std = (sum((v - y_mean) ** 2 for v in y_vals[:n]) / n) ** 0.5

        correlation = cov / (x_std * y_std) if (x_std * y_std) != 0 else Decimal("0")

        return {
            "entity_id": entity_id,
            "period": period,
            "indicator_x": data[codes[0]]["name"],
            "indicator_y": data[codes[1]]["name"],
            "correlation": float(correlation),
            "interpretation": self._interpret_correlation(float(correlation)),
        }

    def _interpret_correlation(self, r: float) -> str:
        """Interpreta el coeficiente de correlación."""
        if r >= 0.7:
            return "correlacion_fuerte_positiva"
        elif r >= 0.3:
            return "correlacion_moderada_positiva"
        elif r >= -0.3:
            return "correlacion_debil_o_ninguna"
        elif r >= -0.7:
            return "correlacion_moderada_negativa"
        else:
            return "correlacion_fuerte_negativa"

    def estimate_next_period(
        self, entity_id: int, indicator_code: str
    ) -> Dict[str, Any]:
        """Estima el valor del próximo período usando regresión lineal simple.

        Args:
            entity_id: ID de la entidad.
            indicator_code: código del indicador.
        Returns:
            dict con 'estimated_value', 'trend', 'confidence'.
        """
        try:
            indicator = Indicator.objects.get(code=indicator_code, is_active=True)
        except Indicator.DoesNotExist:
            return {"error": "Indicador no encontrado"}

        records = (
            IndicatorRecord.objects
            .filter(
                entity_id=entity_id,
                indicator=indicator,
                is_active=True,
            )
            .select_related("period")
            .order_by("period__year")
            .values("period__year", "value")
        )

        records_list = list(records)
        if len(records_list) < 2:
            return {"error": "Datos insuficientes para estimación", "available": len(records_list)}

        years = [r["period__year"] for r in records_list]
        values = [Decimal(str(r["value"])) for r in records_list]

        n = len(years)
        x_mean = sum(years) / n
        y_mean = sum(values) / n

        numerator = sum((years[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((years[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return {"error": "Varianza cero en años"}

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        next_year = max(years) + 1
        estimated = slope * next_year + intercept

        residuals = [values[i] - (slope * years[i] + intercept) for i in range(n)]
        ss_res = sum(r ** 2 for r in residuals)
        ss_tot = sum((v - y_mean) ** 2 for v in values)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        trend = "ascendente" if slope > 0 else "descendente"

        return {
            "indicator_code": indicator_code,
            "entity_id": entity_id,
            "next_period": next_year,
            "estimated_value": float(estimated),
            "trend": trend,
            "slope": float(slope),
            "r_squared": float(r_squared),
            "confidence": "alta" if r_squared > 0.7 else "media" if r_squared > 0.4 else "baja",
            "data_points": n,
        }

    def validate_payload(self, payload: Dict[str, Any]) -> list[str]:
        """Validaciones de negocio retornando lista de errores."""
        errors = []
        if "period" not in payload:
            errors.append("El campo 'period' es obligatorio")
        else:
            try:
                int(payload["period"])
            except (TypeError, ValueError):
                errors.append("'period' debe ser un año entero")

        if "entity_id" in payload:
            try:
                Entity.objects.get(pk=payload["entity_id"], is_active=True)
            except Entity.DoesNotExist:
                errors.append(f"Entity {payload['entity_id']} no existe o está inactiva")

        if "value" in payload:
            try:
                Decimal(str(payload["value"]))
            except Exception:
                errors.append("'value' debe ser numérico")

        return errors


class IndicatorSelector:
    """Selector: consultas complejas de solo-lectura sobre indicadores."""

    def get_summary_by_entity(self, entity_id: int) -> Dict[str, Any]:
        """Resumen de todos los indicadores de una entidad."""
        summary = (
            IndicatorRecord.objects
            .filter(entity_id=entity_id, is_active=True)
            .select_related("indicator", "period")
            .values(
                "indicator__code",
                "indicator__name",
                "indicator__category",
                "period__year",
            )
            .annotate(
                total=Sum("value"),
                promedio=Avg("value"),
                cantidad=Count("id"),
            )
            .order_by("indicator__category", "period__year")
        )
        return {"entity_id": entity_id, "summary": list(summary)}

    def get_latest_values(self, entity_id: int, limit: int = 10) -> list[Dict[str, Any]]:
        """Últimos valores registrados de una entidad."""
        records = (
            IndicatorRecord.objects
            .filter(entity_id=entity_id, is_active=True)
            .select_related("indicator", "period", "entity")
            .order_by("-period__year", "-id")
            .values(
                "id",
                "indicator__code",
                "indicator__name",
                "period__year",
                "value",
                "variable_name",
            )[:limit]
        )
        return list(records)

    def get_period_comparison(
        self, entity_id: int, indicator_code: str, year_start: int, year_end: int
    ) -> list[Dict[str, Any]]:
        """Compara valores de un indicador entre dos años."""
        records = (
            IndicatorRecord.objects
            .filter(
                entity_id=entity_id,
                indicator__code=indicator_code,
                is_active=True,
                period__year__gte=year_start,
                period__year__lte=year_end,
            )
            .select_related("period")
            .order_by("period__year")
            .values("period__year", "value")
        )
        return list(records)


def get_indicator_summary(queryset) -> Dict[str, Any]:
    """Selector legacy: resumen rápido desde un queryset de Django.

    Para producción usar annotate() directamente (evita N+1).
    """
    total = sum(
        Decimal(str(getattr(obj, "value", 0) or 0)) for obj in queryset.iterator()
    )
    count = queryset.count()
    return {"total": float(total), "count": count}


if __name__ == "__main__":
    expert = IndicatorExpert()
    sample = [
        {"category": "salarios", "entity__name": "Alquízar", "value": "1000.5"},
        {"category": "salarios", "entity__name": "Alquízar", "value": "2500.0"},
        {"category": "produccion", "entity__name": "Alquízar", "value": "5000"},
    ]
    print(expert.compute_accumulated(sample))
