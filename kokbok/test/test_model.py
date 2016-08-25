from kokbok.model import *
import kokbok.conf

import pytest

TEST_DB_CONF = kokbok.conf.get_db_conf().copy()
TEST_DB_NAME = TEST_DB_CONF['db']
print(TEST_DB_NAME)


@pytest.fixture(scope="function")
def test_db(request):
    import MySQLdb

    print("CALLED SETUP!")

    conf = TEST_DB_CONF.copy()
    conf.pop('db')

    db_init()

    def teardown_db():
        with MySQLdb.connect(**TEST_DB_CONF) as cursor:
            cursor.execute("DROP DATABASE IF EXISTS %s" % TEST_DB_NAME)

    request.addfinalizer(teardown_db)


def test_ingredient_save(test_db):
    name = "name"
    price = 1
    energy = 2
    fat = 3
    protein = 4
    carbohydrate = 5
    gramspermilliliter = 6
    gramsperunit = 7

    ingredient = Ingredient(name, price, energy, fat, protein, carbohydrate,
                            gramspermilliliter, gramsperunit)

    ingredient.save()
    assert ingredient._id is not None
    same_ingredient = Ingredient.by_id(ingredient._id)

    assert same_ingredient.name == name
    assert same_ingredient.price == price
    assert same_ingredient.energy == energy
    assert same_ingredient.fat == fat
    assert same_ingredient.protein == protein
    assert same_ingredient.carbohydrate == carbohydrate
    assert same_ingredient.gramspermilliliter == gramspermilliliter
    assert same_ingredient.gramsperunit == gramsperunit

    # Behaviour of __eq__-method unknown...
    assert ingredient.__eq__(same_ingredient)


def test_ingredient_delete(test_db):
    name = "name"
    price = 1
    energy = 2
    fat = 3
    protein = 4
    carbohydrate = 5
    gramspermilliliter = 6
    gramsperunit = 7

    ingredient = Ingredient(name, price, energy, fat, protein, carbohydrate,
                            gramspermilliliter, gramsperunit)

    ingredient.save()
    ingredient.delete()

    with pytest.raises(NotFoundException):
        Ingredient.by_id(ingredient._id)


def test_is_subclass():
    assert issubclass(Ingredient, CookBookObject)

def test_new_recipe(test_db):
    ingredient = Ingredient("Test", 1, 2, 3, 4, 5, 6, 7)
    ingredient.save()
    
    recipe = Recipe.new(
            title="bread",
            servings=4,
            cook_time_prep=30,
            cook_time_cook=30,
            ingredients=[{'title': '',
                          'ingredients': [{'unit': Unit.ML, 'quantity': 17, 'prepnotes': None,
                                           'ingredient': ingredient}]}],
            author=None,
            instructions=["Blanda mjöl", "sätt på ugnen", "klart!"],
            description="Jättegott bröd",
            version=1
            )

    same_recipe = Recipe.by_id(recipe._id)
    print(recipe.__str__())
    print(same_recipe.__str__())
    #print(recipe.__dict__)
    #print(same_recipe.__dict__)

    #assert(recipe.__dict__ == same_recipe.__dict__)
    
    assert(recipe == same_recipe)
    

