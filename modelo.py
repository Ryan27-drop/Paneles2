from pulp import *


# ─── DATOS FIJOS DE PANELES ────────────────────────────────────────────────────
PANELES = {
    'A': {'watts': 400, 'area': 1.9, 'costo': 190},
    'B': {'watts': 450, 'area': 2.1, 'costo': 205},
    'C': {'watts': 550, 'area': 2.5, 'costo': 255},
}

HORAS_SOL = 4.5   # horas pico solares por día (constante del modelo)
DIAS_MES  = 30


def resolver_casa(
    consumo_mensual_kwh: float,
    area_techo_m2: float,
    nombre_casa: str = "Casa"
) -> dict:
    """
    Resuelve el ILP de minimización de inversión en paneles solares para una casa.

    Parámetros
    ----------
    consumo_mensual_kwh : float
        Consumo mensual del hogar en kWh.
    area_techo_m2 : float
        Área disponible del techo en m².
    nombre_casa : str
        Etiqueta para identificar la casa en los resultados.

    Retorna
    -------
    dict con:
        estado        : str   ('Óptimo', 'Infactible', 'Error')
        paneles       : dict  {tipo: cantidad}
        costo_total   : float
        produccion_diaria_kwh  : float
        produccion_mensual_kwh : float
        area_usada_m2 : float
        detalle       : list[dict]  (fila por tipo de panel)
    """
    consumo_diario   = consumo_mensual_kwh / DIAS_MES
    produccion_min   = consumo_diario / HORAS_SOL * 1000  # W mínimos instalados

    modelo = LpProblem(f'Paneles_{nombre_casa}', LpMinimize)

    # Variables enteras ≥ 0
    vars_panel = {
        tipo: LpVariable(f'n{tipo}_{nombre_casa}', lowBound=0, cat='Integer')
        for tipo in PANELES
    }

    # ── Función objetivo: minimizar costo total de paneles ─────────────────────
    modelo += lpSum(
        PANELES[t]['costo'] * vars_panel[t]
        for t in PANELES
    ), 'Costo_Total'

    # ── Restricción 1: producción diaria ≥ consumo diario ─────────────────────
    # Σ(watts_i * n_i) * horas_sol / 1000 ≥ consumo_diario_kWh
    modelo += (
        lpSum(PANELES[t]['watts'] * vars_panel[t] for t in PANELES)
        * HORAS_SOL / 1000
        >= consumo_diario
    ), 'Prod_Diaria'

    # ── Restricción 2: producción mensual ≥ consumo mensual ───────────────────
    modelo += (
        lpSum(PANELES[t]['watts'] * vars_panel[t] for t in PANELES)
        * HORAS_SOL / 1000 * DIAS_MES
        >= consumo_mensual_kwh
    ), 'Prod_Mensual'

    # ── Restricción 3: área de paneles ≤ área del techo ───────────────────────
    modelo += (
        lpSum(PANELES[t]['area'] * vars_panel[t] for t in PANELES)
        <= area_techo_m2
    ), 'Area_Techo'

    # ── Restricción 4: potencia instalada ≥ producción mínima en W ────────────
    modelo += (
        lpSum(PANELES[t]['watts'] * vars_panel[t] for t in PANELES)
        >= produccion_min
    ), 'Potencia_Minima'

    # ── Resolver ───────────────────────────────────────────────────────────────
    modelo.solve(PULP_CBC_CMD(msg=0))

    estado_map = {
        1: 'Óptimo',
        -1: 'Infactible',
        -2: 'Sin acotamiento',
        0: 'Sin solución',
    }
    estado = estado_map.get(modelo.status, 'Error')

    if modelo.status != 1:
        return {
            'estado': estado,
            'paneles': {t: 0 for t in PANELES},
            'costo_total': 0,
            'produccion_diaria_kwh': 0,
            'produccion_mensual_kwh': 0,
            'area_usada_m2': 0,
            'detalle': [],
        }

    cantidades = {t: int(vars_panel[t].varValue) for t in PANELES}

    watts_totales       = sum(PANELES[t]['watts'] * cantidades[t] for t in PANELES)
    prod_diaria         = watts_totales * HORAS_SOL / 1000
    prod_mensual        = prod_diaria * DIAS_MES
    area_usada          = sum(PANELES[t]['area'] * cantidades[t] for t in PANELES)
    costo_total         = value(modelo.objective)

    detalle = [
        {
            'Tipo': t,
            'Watts': PANELES[t]['watts'],
            'Área (m²)': PANELES[t]['area'],
            'Costo unitario ($)': PANELES[t]['costo'],
            'Cantidad': cantidades[t],
            'Subtotal ($)': PANELES[t]['costo'] * cantidades[t],
            'Potencia aportada (W)': PANELES[t]['watts'] * cantidades[t],
        }
        for t in PANELES
        if cantidades[t] > 0
    ]

    return {
        'estado': estado,
        'paneles': cantidades,
        'costo_total': costo_total,
        'produccion_diaria_kwh': round(prod_diaria, 3),
        'produccion_mensual_kwh': round(prod_mensual, 2),
        'area_usada_m2': round(area_usada, 2),
        'detalle': detalle,
    }


def resolver_todas(casas: list[dict]) -> dict:
    """
    Resuelve el modelo para N casas y devuelve resultados individuales + resumen global.

    casas: lista de dicts con keys 'nombre', 'consumo_mensual_kwh', 'area_techo_m2'
    """
    resultados = {}
    costo_global = 0

    for casa in casas:
        res = resolver_casa(
            consumo_mensual_kwh=casa['consumo_mensual_kwh'],
            area_techo_m2=casa['area_techo_m2'],
            nombre_casa=casa['nombre'],
        )
        resultados[casa['nombre']] = res
        costo_global += res['costo_total']

    resultados['__global__'] = {'costo_total': costo_global}
    return resultados
