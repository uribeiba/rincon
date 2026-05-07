# reportes/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils.dateparse import parse_date

import json
from collections import defaultdict

from ventas.models import Venta
from compras.models import Compra
from gastos.models import Gasto, TipoGasto
from productos.models import Producto


# =========================================
# DASHBOARD PRINCIPAL
# =========================================
@login_required
def dashboard(request):

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    fecha_inicio_dt = parse_date(fecha_inicio) if fecha_inicio else None
    fecha_fin_dt = parse_date(fecha_fin) if fecha_fin else None

    # =========================================
    # QUERYSETS
    # =========================================
    ventas_qs = Venta.objects.all()
    compras_qs = Compra.objects.all()
    gastos_qs = Gasto.objects.all()

    if fecha_inicio_dt and fecha_fin_dt:

        ventas_qs = ventas_qs.filter(
            fecha__range=[fecha_inicio_dt, fecha_fin_dt]
        )

        compras_qs = compras_qs.filter(
            fecha__range=[fecha_inicio_dt, fecha_fin_dt]
        )

        gastos_qs = gastos_qs.filter(
            fecha__range=[fecha_inicio_dt, fecha_fin_dt]
        )

    # =========================================
    # TOTALES
    # =========================================
    total_ventas = float(
        ventas_qs.aggregate(
            total=Sum('total')
        )['total'] or 0
    )

    total_compras = float(
        compras_qs.aggregate(
            total=Sum('total')
        )['total'] or 0
    )

    total_gastos = float(
        gastos_qs.aggregate(
            total=Sum('monto')
        )['total'] or 0
    )

    # =========================================
    # GASTOS FIJOS / VARIABLES
    # =========================================
    gastos_fijos = 0.0
    gastos_variables = 0.0

    if TipoGasto.objects.filter(tipo='fijo').exists():

        gastos_fijos = float(
            gastos_qs.filter(
                tipo_gasto__tipo='fijo'
            ).aggregate(
                total=Sum('monto')
            )['total'] or 0
        )

    if TipoGasto.objects.filter(tipo='variable').exists():

        gastos_variables = float(
            gastos_qs.filter(
                tipo_gasto__tipo='variable'
            ).aggregate(
                total=Sum('monto')
            )['total'] or 0
        )

    # =========================================
    # UTILIDAD GENERAL
    # =========================================
    utilidad = (
        total_ventas
        - total_compras
        - total_gastos
    )

    # =========================================
    # VENTAS POR DÍA
    # =========================================
    ventas_por_dia = defaultdict(float)

    for v in ventas_qs:
        ventas_por_dia[v.fecha.isoformat()] += float(v.total)

    gastos_por_dia = defaultdict(float)

    for g in gastos_qs:
        gastos_por_dia[g.fecha.isoformat()] += float(g.monto)

    compras_por_dia = defaultdict(float)

    for c in compras_qs:
        compras_por_dia[c.fecha.isoformat()] += float(c.total)

    ventas_lista = [
        {
            'dia': d,
            'total': ventas_por_dia[d]
        }
        for d in sorted(ventas_por_dia.keys())
    ]

    gastos_lista = [
        {
            'dia': d,
            'total': gastos_por_dia[d]
        }
        for d in sorted(gastos_por_dia.keys())
    ]

    compras_lista = [
        {
            'dia': d,
            'total': compras_por_dia[d]
        }
        for d in sorted(compras_por_dia.keys())
    ]

    # =========================================
    # UTILIDAD POR DÍA
    # =========================================
    todas_fechas = (
        set(ventas_por_dia.keys())
        | set(gastos_por_dia.keys())
        | set(compras_por_dia.keys())
    )

    utilidad_por_dia = []

    for fecha in sorted(todas_fechas):

        util = (
            ventas_por_dia[fecha]
            - compras_por_dia[fecha]
            - gastos_por_dia[fecha]
        )

        utilidad_por_dia.append({
            'dia': fecha,
            'utilidad': util
        })

    # =========================================
    # RENTABILIDAD POR PRODUCTO
    # =========================================
    rentabilidad_lista = []

    # =========================================
    # COSTEO INTELIGENTE
    # =========================================
    productos = Producto.objects.all().select_related(
        'categoria'
    )

    costeo_productos = []

    for p in productos:

        costo = float(p.costo or 0)

        gastos_fijos_producto = p.gastos_fijos()

        gastos_variables_producto = p.gastos_variables()

        costo_real = p.costo_real()

        iva_porc = p.iva_porcentaje()

        iva_monto = p.iva_monto()

        costo_con_iva = p.costo_con_iva()

        precio_sugerido = p.precio_sugerido()

        ganancia_pesos = p.ganancia_pesos()

        ganancia_porc = p.ganancia_porcentaje()

        costeo_productos.append({

            'nombre': p.nombre,

            'costo_kg': round(costo, 2),

            'gastos_fijos_kg': round(
                gastos_fijos_producto,
                2
            ),

            'gastos_variables_kg': round(
                gastos_variables_producto,
                2
            ),

            'costo_real_kg': round(
                costo_real,
                2
            ),

            'iva_porcentaje': round(
                iva_porc,
                2
            ),

            'iva_monto': round(
                iva_monto,
                2
            ),

            'costo_con_iva': round(
                costo_con_iva,
                2
            ),

            'precio_sugerido': round(
                precio_sugerido,
                2
            ),

            'ganancia_pesos': round(
                ganancia_pesos,
                2
            ),

            'ganancia_porcentaje': round(
                ganancia_porc,
                2
            )
        })

    # =========================================
    # ALERTAS Y RECOMENDACIONES
    # =========================================
    alertas = []

    recomendaciones = []

    for r in rentabilidad_lista:

        if r['utilidad'] < 0:

            alertas.append(
                f"❌ {r['producto']} pérdidas (${r['utilidad']:.0f})"
            )

            recomendaciones.append(
                f"Revisar costos de {r['producto']}"
            )

        elif r['margen'] < 10:

            alertas.append(
                f"⚠ {r['producto']} margen bajo ({r['margen']}%)"
            )

            recomendaciones.append(
                f"Subir margen objetivo de {r['producto']}"
            )

        elif r['margen'] > 40:

            recomendaciones.append(
                f"🔥 Potenciar ventas de {r['producto']}"
            )

    if total_gastos > (total_ventas * 0.5):

        alertas.append(
            "💸 Gastos superan 50% de ventas"
        )

        recomendaciones.append(
            "Reducir gastos operacionales"
        )

    if utilidad < 0:

        recomendaciones.append(
            "⚠ Negocio en pérdida"
        )

    else:

        recomendaciones.append(
            "✅ Negocio rentable"
        )

    # =========================================
    # SCORE FINANCIERO
    # =========================================
    score = 0

    if total_ventas > 0:

        margen_total = (
            utilidad / total_ventas
        ) * 100

        if margen_total > 30:
            score += 50

        elif margen_total > 15:
            score += 35

        elif margen_total > 0:
            score += 20

        else:
            score += 5

        ratio_gastos = (
            total_gastos / total_ventas
        )

        if ratio_gastos < 0.3:
            score += 30

        elif ratio_gastos < 0.5:
            score += 20

        else:
            score += 5

    if score > 80:
        nivel = "Excelente"

    elif score > 60:
        nivel = "Bueno"

    elif score > 40:
        nivel = "Regular"

    else:
        nivel = "Crítico"

    # =========================================
    # CONTEXT
    # =========================================
    context = {

        'ventas': round(total_ventas, 2),

        'compras': round(total_compras, 2),

        'gastos': round(total_gastos, 2),

        'utilidad': round(utilidad, 2),

        'gastos_fijos': round(gastos_fijos, 2),

        'gastos_variables': round(gastos_variables, 2),

        'ventas_data': json.dumps(
            ventas_lista,
            default=str
        ),

        'gastos_data': json.dumps(
            gastos_lista,
            default=str
        ),

        'compras_data': json.dumps(
            compras_lista,
            default=str
        ),

        'utilidad_data': json.dumps(
            utilidad_por_dia,
            default=str
        ),

        'rentabilidad': rentabilidad_lista,

        'costeo_productos': costeo_productos,

        'alertas': alertas,

        'recomendaciones': recomendaciones,

        'score': score,

        'nivel': nivel,

        'fecha_inicio': fecha_inicio,

        'fecha_fin': fecha_fin,
    }

    return render(
        request,
        'dashboard.html',
        context
    )