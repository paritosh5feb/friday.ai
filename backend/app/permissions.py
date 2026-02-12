from collections.abc import Iterable

from .models import ProjectMember

PROJECT_SCOPES = [
    "manage_members",
    "manage_lifecycle",
    "manage_experiments",
    "manage_runs",
    "manage_tasks",
    "manage_pages",
]

ROLE_DEFAULT_SCOPES: dict[str, list[str]] = {
    "admin": PROJECT_SCOPES,
    "manager": ["manage_lifecycle", "manage_experiments", "manage_runs", "manage_tasks", "manage_pages"],
    "researcher": ["manage_lifecycle", "manage_experiments", "manage_runs", "manage_tasks"],
    "reviewer": ["manage_pages", "manage_tasks"],
    "viewer": [],
}


def parse_scopes(scope_string: str | None) -> list[str]:
    if not scope_string:
        return []
    seen: set[str] = set()
    normalized: list[str] = []
    for item in scope_string.split(","):
        scope = item.strip()
        if scope and scope in PROJECT_SCOPES and scope not in seen:
            seen.add(scope)
            normalized.append(scope)
    return normalized


def serialize_scopes(scopes: Iterable[str]) -> str:
    seen: set[str] = set()
    normalized: list[str] = []
    for scope in scopes:
        if scope in PROJECT_SCOPES and scope not in seen:
            seen.add(scope)
            normalized.append(scope)
    return ",".join(normalized)


def normalize_member_scopes(role: str, requested_scopes: list[str] | None) -> list[str]:
    if requested_scopes is None:
        return ROLE_DEFAULT_SCOPES.get(role, [])
    return [scope for scope in requested_scopes if scope in PROJECT_SCOPES]


def effective_member_scopes(member: ProjectMember | None) -> set[str]:
    if member is None:
        # Owners are treated as full-access actors.
        return set(PROJECT_SCOPES)
    if member.scopes:
        return set(parse_scopes(member.scopes))
    return set(ROLE_DEFAULT_SCOPES.get(member.role, []))


def has_scope(member: ProjectMember | None, scope: str) -> bool:
    return scope in effective_member_scopes(member)
