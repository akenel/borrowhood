"""user_api/ — Users API split by domain.

Previously one 1,090-line users.py file. Now a package where each
sub-module owns a subset of /api/v1/users/* endpoints. Registration
order matters: /me* and favorites BEFORE /{user_id} to avoid UUID
path collisions.

main.py still does `from src.routers import users` (via shim). The
shim re-exports this package's router.
"""

from fastapi import APIRouter

from . import me, favorites, gdpr, members, skills
# Re-export for tests that import specific handlers or schemas
from .me import get_current_user, update_me  # noqa: F401
from .members import list_members  # noqa: F401
from .gdpr import delete_my_account  # noqa: F401
from .skills import SkillCreate  # noqa: F401

router = APIRouter(prefix="/api/v1/users", tags=["users"])

# Order matters: /me* and favorites (explicit paths) BEFORE /{user_id} (wildcard)
router.include_router(me.router)
router.include_router(favorites.router)
router.include_router(gdpr.router)
router.include_router(skills.router)
# Members last — contains /{user_id} wildcard route
router.include_router(members.router)
