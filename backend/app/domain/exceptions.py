class DomainError(Exception):
    """Base class for all domain-level errors."""


class NotFoundError(DomainError):
    def __init__(self, entity_name: str, entity_id: object):
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(f"{entity_name} con id={entity_id} no encontrado")


class DuplicateError(DomainError):
    def __init__(self, entity_name: str, field: str, value: object):
        self.entity_name = entity_name
        self.field = field
        self.value = value
        super().__init__(f"{entity_name} con {field}={value} ya existe")


class InvalidCredentialsError(DomainError):
    def __init__(self):
        super().__init__("Credenciales inválidas")


class InsufficientStockError(DomainError):
    def __init__(self, product_id: object, requested: object, available: object):
        self.product_id = product_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Stock insuficiente para el producto {product_id}: "
            f"solicitado={requested}, disponible={available}"
        )


class InvalidOperationError(DomainError):
    def __init__(self, message: str):
        super().__init__(message)


class UnbalancedEntryError(DomainError):
    def __init__(self, total_debit: object, total_credit: object):
        self.total_debit = total_debit
        self.total_credit = total_credit
        super().__init__(
            f"Asiento contable descuadrado: debitos={total_debit}, creditos={total_credit}"
        )
