import json
import re
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from .models import Compra, Proveedor


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def _clean_rut(value):
    """Normaliza un RUT chileno para compararlo de forma consistente."""
    if not value:
        return ""

    rut = str(value).strip().upper()
    rut = rut.replace(".", "").replace(" ", "")
    return rut


def _money(value):
    """Convierte un monto recibido desde el TED a Decimal."""
    if value in (None, ""):
        return Decimal("0")

    text = str(value).strip().replace(".", "").replace(",", ".")

    try:
        return Decimal(text)
    except InvalidOperation:
        return Decimal("0")


def _xml_value(node, path):
    """Obtiene el texto de un nodo TED sin romper si no existe."""
    found = node.find(path)
    if found is None or found.text is None:
        return ""
    return found.text.strip()


# =========================================================
# PARSER DEL TED (tolerante a caracteres corruptos del lector)
# =========================================================

def _extract_ted_field(raw, tag):
    """
    Extrae un campo del TED crudo.

    Acepta tanto XML normal:
        <TAG>valor</TAG>
    como el formato corrupto por layout de teclado:
        TAG:valor;TAG:
        TAG;valor:TAG;
    """
    # Patrón 1: TAG[:;](valor)[:;]TAG   → tag de apertura y cierre
    pattern_close = rf'{tag}[:;]([^:;]+)[:;]{tag}'
    match = re.search(pattern_close, raw, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Patrón 2: TAG[:;](valor)  → solo tag de apertura
    pattern_open = rf'{tag}[:;]([^:;]+)'
    match = re.search(pattern_open, raw, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return ""


def _normalize_date(value):
    """Normaliza la fecha del TED, tolerando separadores corruptos."""
    if not value:
        return ""
    # El lector a veces envía ' o / en lugar de -
    return value.replace("'", "-").replace("/", "-").strip()


def parse_ted(raw_ted):
    """
    Interpreta el XML contenido dentro del PDF417 del timbre electrónico SII.

    Soporta dos escenarios:
      1. XML bien formado (cuando el lector está configurado correctamente).
      2. Texto con caracteres corruptos por layout de teclado
         (ej: '<' → ';', '>' → ':', '/' → '-', '-' → "'").

    El TED del SII contiene, entre otros:
      RE  = RUT emisor
      TD  = tipo DTE
      F   = folio
      FE  = fecha emisión
      RR  = RUT receptor
      RSR = razón social receptor
      MNT = monto total
      IT1 = primer ítem
    """
    if not raw_ted:
        raise ValueError("No se recibió información del código PDF417.")

    raw = str(raw_ted).strip()

    # Limpiar caracteres de control no imprimibles
    raw = ''.join(
        ch for ch in raw
        if ch in '\n\r\t' or ord(ch) >= 32
    )

    # ---------------------------------------------------------
    # Intento 1: XML estándar (lector bien configurado)
    # ---------------------------------------------------------
    if '<TED' in raw and '</TED>' in raw:
        try:
            return _parse_ted_xml(raw)
        except (ValueError, ET.ParseError):
            # Si el XML está mal formado, caemos al parser tolerante
            pass

    # ---------------------------------------------------------
    # Intento 2: Parser tolerante (caracteres corruptos)
    # ---------------------------------------------------------
    return _parse_ted_tolerant(raw)


def _parse_ted_xml(raw):
    """Parser estricto para TED bien formado (XML válido)."""
    start = raw.find("<TED")
    end = raw.rfind("</TED>")

    if start == -1 or end == -1:
        raise ValueError("El código no contiene un TED del SII.")

    xml_text = raw[start:end + len("</TED>")]
    xml_text = xml_text.replace("\x00", "")

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ValueError("El TED no tiene un XML válido.") from exc

    dd = root.find("DD")
    if dd is None:
        raise ValueError("El TED no contiene el bloque DD esperado.")

    rut_emisor = _clean_rut(_xml_value(dd, "RE"))
    tipo_dte = _xml_value(dd, "TD")
    folio = _xml_value(dd, "F")
    fecha = _xml_value(dd, "FE")
    rut_receptor = _clean_rut(_xml_value(dd, "RR"))
    receptor = _xml_value(dd, "RSR")
    total = _money(_xml_value(dd, "MNT"))
    primer_item = _xml_value(dd, "IT1")

    return _build_ted_result(
        rut_emisor=rut_emisor,
        tipo_dte=tipo_dte,
        folio=folio,
        fecha=fecha,
        rut_receptor=rut_receptor,
        receptor=receptor,
        total=total,
        primer_item=primer_item,
        raw=raw,
    )


def _parse_ted_tolerant(raw):
    """
    Parser tolerante: extrae los campos con regex sin pretender
    reconstruir el XML. Funciona cuando el lector envía caracteres
    corruptos por layout de teclado.
    """
    rut_emisor = _clean_rut(_extract_ted_field(raw, "RE"))
    tipo_dte = _extract_ted_field(raw, "TD")
    folio = _extract_ted_field(raw, "F")
    fecha = _normalize_date(_extract_ted_field(raw, "FE"))
    rut_receptor = _clean_rut(_extract_ted_field(raw, "RR"))
    receptor = _extract_ted_field(raw, "RSR")
    total_str = _extract_ted_field(raw, "MNT")
    primer_item = _extract_ted_field(raw, "IT1")

    total = _money(total_str)

    return _build_ted_result(
        rut_emisor=rut_emisor,
        tipo_dte=tipo_dte,
        folio=folio,
        fecha=fecha,
        rut_receptor=rut_receptor,
        receptor=receptor,
        total=total,
        primer_item=primer_item,
        raw=raw,
    )


def _build_ted_result(
    rut_emisor,
    tipo_dte,
    folio,
    fecha,
    rut_receptor,
    receptor,
    total,
    primer_item,
    raw,
):
    """Construye el diccionario de resultado y hace las validaciones finales."""
    if not rut_emisor or not tipo_dte or not folio or not fecha:
        raise ValueError(
            f"Faltan datos principales del DTE. "
            f"RUT emisor: '{rut_emisor}', tipo: '{tipo_dte}', "
            f"folio: '{folio}', fecha: '{fecha}'."
        )

    fecha_valida = parse_date(fecha)
    if not fecha_valida:
        raise ValueError(f"La fecha del DTE no es válida: {fecha}")

    tipo_dte_int = int(tipo_dte) if tipo_dte.isdigit() else 0

    # En esta primera etapa usamos las categorías que ya existen en Compra.
    if tipo_dte_int in (39, 41):
        tipo_documento = "boleta"
        tipo_documento_label = "Boleta electrónica"
    elif tipo_dte_int in (33, 34):
        tipo_documento = "factura"
        tipo_documento_label = "Factura electrónica"
    else:
        tipo_documento = "factura"
        tipo_documento_label = f"DTE tipo {tipo_dte}"

    proveedor = Proveedor.objects.filter(rut__iexact=rut_emisor).first()

    duplicate = None
    if proveedor:
        duplicate = (
            Compra.objects
            .filter(
                proveedor=proveedor,
                tipo_documento=tipo_documento,
                numero_documento=folio,
            )
            .first()
        )

    return {
        "rut_emisor": rut_emisor,
        "tipo_dte": tipo_dte,
        "tipo_documento": tipo_documento,
        "tipo_documento_label": tipo_documento_label,
        "folio": folio,
        "fecha": fecha,
        "rut_receptor": rut_receptor,
        "receptor": receptor,
        "total": str(total),
        "primer_item": primer_item,
        "proveedor_id": proveedor.id if proveedor else None,
        "proveedor_nombre": proveedor.nombre if proveedor else "",
        "proveedor_nuevo": proveedor is None,
        "duplicada": duplicate is not None,
        "compra_existente_id": duplicate.id if duplicate else None,
        "ted": raw,
    }


# =========================================================
# PANTALLA WEB DE COMPRAS
# =========================================================

@login_required
def compras_view(request):
    compras = (
        Compra.objects
        .select_related("proveedor")
        .order_by("-fecha", "-id")[:30]
    )

    return render(
        request,
        "compras/compras.html",
        {"compras": compras},
    )


# =========================================================
# API: PROCESAR PDF417
# =========================================================

@login_required
@require_POST
def procesar_pdf417(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
        raw_ted = payload.get("ted", "")
        data = parse_ted(raw_ted)
        return JsonResponse({"ok": True, "data": data})

    except json.JSONDecodeError:
        return JsonResponse(
            {"ok": False, "error": "La solicitud no contiene JSON válido."},
            status=400,
        )
    except (ValueError, TypeError) as exc:
        return JsonResponse(
            {"ok": False, "error": str(exc)},
            status=400,
        )


# =========================================================
# API: GUARDAR COMPRA
# =========================================================

@login_required
@require_POST
def guardar_compra_factura(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))

        rut = _clean_rut(payload.get("rut_emisor"))
        nombre = str(payload.get("proveedor_nombre", "")).strip()
        proveedor_id = payload.get("proveedor_id")
        fecha = parse_date(str(payload.get("fecha", "")).strip())
        tipo_documento = str(payload.get("tipo_documento", "factura")).strip()
        numero_documento = str(payload.get("numero_documento", "")).strip()
        observacion = str(payload.get("observacion", "")).strip()
        total = _money(payload.get("total"))

        if not rut:
            return JsonResponse({"ok": False, "error": "Falta el RUT del proveedor."}, status=400)

        if not nombre:
            return JsonResponse({"ok": False, "error": "Falta el nombre del proveedor."}, status=400)

        if not fecha:
            return JsonResponse({"ok": False, "error": "La fecha de la factura no es válida."}, status=400)

        if not numero_documento:
            return JsonResponse({"ok": False, "error": "Falta el folio de la factura."}, status=400)

        if total < 0:
            return JsonResponse({"ok": False, "error": "El total no puede ser negativo."}, status=400)

        with transaction.atomic():
            proveedor = None

            if proveedor_id:
                proveedor = Proveedor.objects.filter(id=proveedor_id).first()

            if proveedor is None:
                proveedor = Proveedor.objects.filter(rut__iexact=rut).first()

            if proveedor is None:
                proveedor = Proveedor.objects.create(
                    nombre=nombre,
                    rut=rut,
                )
            else:
                # Si el proveedor existía sin RUT, lo completamos.
                if not proveedor.rut:
                    proveedor.rut = rut
                    proveedor.save(update_fields=["rut"])

            # Evita registrar dos veces la misma factura.
            existente = (
                Compra.objects
                .filter(
                    proveedor=proveedor,
                    tipo_documento=tipo_documento,
                    numero_documento=numero_documento,
                )
                .first()
            )

            if existente:
                return JsonResponse({
                    "ok": False,
                    "duplicate": True,
                    "error": (
                        f"La factura {numero_documento} ya está registrada "
                        f"para {proveedor.nombre}."
                    ),
                    "compra_id": existente.id,
                }, status=409)

            compra = Compra.objects.create(
                proveedor=proveedor,
                fecha=fecha,
                total=total,
                tipo_documento=tipo_documento,
                numero_documento=numero_documento,
                observacion=observacion,
            )

        return JsonResponse({
            "ok": True,
            "compra_id": compra.id,
            "proveedor_id": proveedor.id,
            "mensaje": f"Compra #{compra.id} registrada correctamente.",
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {"ok": False, "error": "La solicitud no contiene JSON válido."},
            status=400,
        )
    except Exception as exc:
        return JsonResponse(
            {"ok": False, "error": f"No se pudo guardar la compra: {exc}"},
            status=500,
        )

# =========================================================
# DIAGNÓSTICO: capturar lo que envía el lector
# =========================================================
@login_required
def diagnostico_lector(request):
    """Página simple para ver el texto crudo del lector."""
    return render(request, "compras/diagnostico_lector.html")