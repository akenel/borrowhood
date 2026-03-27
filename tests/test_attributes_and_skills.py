"""Tests for JSONB attributes, category groups, and skills CRUD.

Covers:
- Attribute schema API endpoints
- Category group filtering
- Item attributes in create/update/response
- Skills CRUD (add, list, delete, batch)
- Skills suggest endpoint (auth gate)
"""

import pytest


# ── Attribute Schema API ──


@pytest.mark.asyncio
async def test_attribute_schemas_endpoint(client):
    """GET /attribute-schemas returns all schemas and groups."""
    resp = await client.get("/api/v1/items/attribute-schemas")
    assert resp.status_code == 200
    data = resp.json()
    assert "schemas" in data
    assert "groups" in data
    assert "vehicles" in data["schemas"]
    assert "property" in data["schemas"]
    assert "jobs" in data["schemas"]
    assert len(data["groups"]) >= 10


@pytest.mark.asyncio
async def test_attribute_schema_vehicles(client):
    """GET /attribute-schema/vehicles returns vehicle fields."""
    resp = await client.get("/api/v1/items/attribute-schema/vehicles")
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "vehicles"
    fields = data["fields"]
    assert "year" in fields
    assert "mileage_km" in fields
    assert "fuel_type" in fields
    assert "transmission" in fields
    assert "euro_class" in fields
    assert fields["fuel_type"]["type"] == "select"
    assert "diesel" in fields["fuel_type"]["options"]


@pytest.mark.asyncio
async def test_attribute_schema_apartment(client):
    """GET /attribute-schema/apartment returns property fields."""
    resp = await client.get("/api/v1/items/attribute-schema/apartment")
    assert resp.status_code == 200
    data = resp.json()
    fields = data["fields"]
    assert "bedrooms" in fields
    assert "bathrooms" in fields
    assert "floor_area_sqm" in fields
    assert "energy_class" in fields
    assert "furnished" in fields
    assert fields["energy_class"]["type"] == "select"


@pytest.mark.asyncio
async def test_attribute_schema_job(client):
    """GET /attribute-schema/job_full_time returns job fields."""
    resp = await client.get("/api/v1/items/attribute-schema/job_full_time")
    assert resp.status_code == 200
    data = resp.json()
    fields = data["fields"]
    assert "job_type" in fields
    assert "salary_min" in fields
    assert "salary_max" in fields
    assert "experience_level" in fields
    assert "remote_option" in fields


@pytest.mark.asyncio
async def test_attribute_schema_unknown_category(client):
    """GET /attribute-schema/unknown returns empty fields."""
    resp = await client.get("/api/v1/items/attribute-schema/power_tools")
    assert resp.status_code == 200
    data = resp.json()
    assert data["fields"] == {}


# ── Category Groups ──


@pytest.mark.asyncio
async def test_category_groups_in_schemas(client):
    """Verify all expected groups exist."""
    resp = await client.get("/api/v1/items/attribute-schemas")
    groups = resp.json()["groups"]
    assert "property" in groups
    assert "vehicles" in groups
    assert "jobs" in groups
    assert "tools_workshop" in groups
    # Property group has the right subcategories
    assert "apartment" in groups["property"]
    assert "house" in groups["property"]
    assert "vacation_rental" in groups["property"]
    # Vehicles group
    assert "vehicles" in groups["vehicles"]
    assert "automotive" in groups["vehicles"]
    # Jobs group
    assert "job_full_time" in groups["jobs"]
    assert "job_freelance" in groups["jobs"]


# ── Attribute Schemas Bilingual Labels ──


@pytest.mark.asyncio
async def test_vehicle_schema_has_italian_labels(client):
    """Vehicle attribute schema includes Italian labels."""
    resp = await client.get("/api/v1/items/attribute-schema/vehicles")
    fields = resp.json()["fields"]
    assert fields["fuel_type"]["label_it"] == "Carburante"
    assert fields["transmission"]["label_it"] == "Cambio"
    assert fields["mileage_km"]["label_it"] == "Chilometraggio (km)"


# ── Skills CRUD (auth-gated) ──


@pytest.mark.asyncio
async def test_list_skills_requires_auth(client):
    """GET /users/me/skills requires auth."""
    resp = await client.get("/api/v1/users/me/skills")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_add_skill_requires_auth(client):
    """POST /users/me/skills requires auth."""
    resp = await client.post("/api/v1/users/me/skills", json={
        "skill_name": "Welding", "category": "welding", "self_rating": 4
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_delete_skill_requires_auth(client):
    """DELETE /users/me/skills/{id} requires auth."""
    resp = await client.delete("/api/v1/users/me/skills/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_batch_skills_requires_auth(client):
    """POST /users/me/skills/batch requires auth."""
    resp = await client.post("/api/v1/users/me/skills/batch", json={
        "skills": [{"skill_name": "Test", "category": "other"}]
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_suggest_skills_requires_auth(client):
    """POST /users/me/skills/suggest requires auth."""
    resp = await client.post("/api/v1/users/me/skills/suggest", json={
        "source": "bio"
    })
    assert resp.status_code == 401


# ── Model/Schema validation ──


@pytest.mark.asyncio
async def test_item_create_accepts_attributes():
    """ItemCreate schema accepts attributes field."""
    from src.schemas.item import ItemCreate
    data = ItemCreate(
        name="Test Car",
        item_type="physical",
        category="vehicles",
        attributes={"year": 2020, "fuel_type": "diesel"}
    )
    assert data.attributes == {"year": 2020, "fuel_type": "diesel"}


@pytest.mark.asyncio
async def test_item_create_accepts_new_categories():
    """ItemCreate accepts property and job categories (no longer enum-restricted)."""
    from src.schemas.item import ItemCreate
    # Property category
    data = ItemCreate(name="Apartment", item_type="space", category="apartment")
    assert data.category == "apartment"
    # Job category
    data2 = ItemCreate(name="Chef", item_type="service", category="job_full_time")
    assert data2.category == "job_full_time"


@pytest.mark.asyncio
async def test_item_out_includes_attributes():
    """ItemOut schema includes attributes field."""
    from src.schemas.item import ItemOut
    assert "attributes" in ItemOut.model_fields


@pytest.mark.asyncio
async def test_get_attribute_schema_function():
    """get_attribute_schema returns correct schema per category."""
    from src.models.item import get_attribute_schema
    v = get_attribute_schema("vehicles")
    assert "year" in v
    assert "fuel_type" in v

    p = get_attribute_schema("apartment")
    assert "bedrooms" in p
    assert "energy_class" in p

    j = get_attribute_schema("job_full_time")
    assert "salary_min" in j

    empty = get_attribute_schema("power_tools")
    assert empty == {}


# ── Skill model ──


@pytest.mark.asyncio
async def test_skill_create_schema():
    """SkillCreate schema validates correctly."""
    from src.routers.users import SkillCreate
    s = SkillCreate(skill_name="TIG Welding", category="welding", self_rating=4, years_experience=10)
    assert s.skill_name == "TIG Welding"
    assert s.self_rating == 4


@pytest.mark.asyncio
async def test_skill_create_rating_bounds():
    """SkillCreate rejects ratings outside 1-5."""
    from src.routers.users import SkillCreate
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        SkillCreate(skill_name="Test", category="other", self_rating=0)
    with pytest.raises(ValidationError):
        SkillCreate(skill_name="Test", category="other", self_rating=6)


@pytest.mark.asyncio
async def test_skill_create_name_too_short():
    """SkillCreate rejects names shorter than 2 chars."""
    from src.routers.users import SkillCreate
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        SkillCreate(skill_name="X", category="other")
