from app.slug import generate_slug


def test_default_length():
    assert len(generate_slug()) == 7


def test_custom_length():
    assert len(generate_slug(12)) == 12


def test_is_random_enough():
    # 50 попыток без единой коллизии — при 62 символах в алфавите это ожидаемо
    slugs = {generate_slug() for _ in range(50)}
    assert len(slugs) == 50
