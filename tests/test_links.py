import pytest


@pytest.mark.asyncio
async def test_create_redirect_and_stats_flow(client):
    created = await client.post("/links", json={"target_url": "https://example.com"})
    assert created.status_code == 201
    slug = created.json()["slug"]

    # 307, а не 200 — редирект не должен сам ходить по ссылке, это делает браузер
    redirected = await client.get(f"/{slug}", follow_redirects=False)
    assert redirected.status_code == 307
    assert redirected.headers["location"] == "https://example.com/"

    stats = await client.get(f"/links/{slug}/stats")
    assert stats.json()["total_clicks"] == 1


@pytest.mark.asyncio
async def test_unknown_slug_is_404(client):
    response = await client.get("/this-slug-does-not-exist")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_rate_limit_blocks_burst(client):
    for _ in range(5):  # rate_limit_max_requests по умолчанию = 5
        ok = await client.post("/links", json={"target_url": "https://example.com"})
        assert ok.status_code == 201

    blocked = await client.post("/links", json={"target_url": "https://example.com"})
    assert blocked.status_code == 429
