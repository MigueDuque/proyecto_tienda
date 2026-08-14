"""Chart-of-accounts codes used by the seed data and the accounting service.

Kept as a single source of truth so the seed script and AccountingService
never hardcode the codes independently.
"""

CAJA = "1105"
BANCOS = "1110"
INVENTARIO = "1435"
CUENTAS_POR_COBRAR = "1305"
CUENTAS_POR_PAGAR = "2205"
VENTAS = "4135"
COSTO_DE_VENTAS = "6135"
GASTOS = "5195"

SEED_ACCOUNTS = [
    (CAJA, "Caja", "ACTIVO"),
    (BANCOS, "Bancos", "ACTIVO"),
    (INVENTARIO, "Inventario", "ACTIVO"),
    (CUENTAS_POR_COBRAR, "Cuentas por Cobrar", "ACTIVO"),
    (CUENTAS_POR_PAGAR, "Cuentas por Pagar", "PASIVO"),
    (VENTAS, "Ventas", "INGRESO"),
    (COSTO_DE_VENTAS, "Costo de Ventas", "COSTO"),
    (GASTOS, "Gastos", "GASTO"),
]
