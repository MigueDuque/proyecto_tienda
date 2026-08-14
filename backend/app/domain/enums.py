from enum import Enum


class PartnerType(str, Enum):
    CLIENTE = "CLIENTE"
    PROVEEDOR = "PROVEEDOR"
    AMBOS = "AMBOS"


class PaymentMethod(str, Enum):
    CONTADO = "CONTADO"
    CREDITO = "CREDITO"


class MovementType(str, Enum):
    ENTRADA_COMPRA = "ENTRADA_COMPRA"
    SALIDA_VENTA = "SALIDA_VENTA"
    AJUSTE_ENTRADA = "AJUSTE_ENTRADA"
    AJUSTE_SALIDA = "AJUSTE_SALIDA"


class MovementReferenceType(str, Enum):
    PURCHASE = "PURCHASE"
    SALE = "SALE"
    ADJUSTMENT = "ADJUSTMENT"


class AccountType(str, Enum):
    ACTIVO = "ACTIVO"
    PASIVO = "PASIVO"
    PATRIMONIO = "PATRIMONIO"
    INGRESO = "INGRESO"
    GASTO = "GASTO"
    COSTO = "COSTO"


class JournalEntryReferenceType(str, Enum):
    SALE = "SALE"
    PURCHASE = "PURCHASE"
    MANUAL = "MANUAL"
