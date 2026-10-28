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


class DiscoveryError(RuntimeError):
    """A discovery provider could not produce a trustworthy result."""


class DiscoveryRestrictedError(DiscoveryError):
    """The target requires access not permitted by the anonymous boundary."""


class DiscoveryRateLimitError(DiscoveryError):
    """The provider refused the request because of rate limiting."""


class DiscoveryContractError(DiscoveryError):
    """Provider output no longer satisfies the expected contract."""
