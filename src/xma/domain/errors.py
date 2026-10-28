"""Small, actionable errors raised by domain and catalog boundaries."""


class DomainError(ValueError):
    """Base class for invalid domain data."""


class InvalidIdentityError(DomainError):
    """An external or compound identity is invalid."""


class InvalidTransitionError(DomainError):
    """A download job transition is not allowed."""


class IdentityConflictError(DomainError):
    """Persisted identity conflicts with the supplied aggregate."""


class CatalogError(RuntimeError):
    """The catalog could not complete an operation."""
