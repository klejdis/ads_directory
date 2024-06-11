from quart.testing import QuartClient

from ads_directory.config import settings

BASE_PATH = settings.base_path


async def test_create_category(client: QuartClient, migrated_database) -> None:
    response = await client.post(
        f"{BASE_PATH}/categories/", json={"name": "test_category", "description": "RealEstate", "custom_fields": [1]}
    )

    assert response.status_code == 200
