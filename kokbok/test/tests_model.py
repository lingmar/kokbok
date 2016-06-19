from kokbok.model import Ingredient, CookBookObject


def test_ingredient_save():
    assert issubclass(Ingredient, CookBookObject)
