import MySQLdb
from _mysql_exceptions import IntegrityError

from abc import ABCMeta, abstractmethod

import kokbok.conf


global dbconf
dbconf = kokbok.conf.get_db_conf()


def db_init():
    """
    Initialise a new (clean) database.
    """
    conf_no_db_name = dbconf.copy()
    conf_no_db_name.pop('db')

    with MySQLdb.connect(**conf_no_db_name) as cursor:
        with open('kokbok.sql') as x:
            for line in x.read().split(';\n'):
                if len(line.strip()) > 0:
                    cursor.execute(line % {'dbname': dbconf['db']})

class CookBookObject(metaclass=ABCMeta):

    @abstractmethod
    def save(self) -> None:
        """
        Save the current object to the database. Add it if not present,
        otherwise update it.
        """
        return NotImplemented

    @classmethod
    @abstractmethod
    def by_id(cls, _id):
        """
        Return a new object of the current type by its ID. Raises an
        Exception if ID is not present.
        """
        return NotImplemented

    @abstractmethod
    def delete(self) -> None:
        """
        Permanently delete the current object from the database (if
        present). Otherwise do nothing.
        """
        return NotImplemented

    @abstractmethod
    def refresh(self) -> None:
        """
        Refresh the current object from the database, overwriting any
        altered values. Raises an Exception ??? if no longer present.
        """
        return NotImplemented

    def execute_one(self, query, arglist):
        with MySQLdb.connect(**dbconf) as cursor:
            cursor.execute(query, arglist)

            cursor.execute("SELECT LAST_INSERT_ID()")
            return cursor.fetchone()[0]

    def execute_many(self, query, arglist):
        with MySQLdb.connect(**dbconf) as cursor:
            cursor.execute_many(query, arglist)
            return cursor.fetchone()


class Ingredient(CookBookObject):

    def __init__(self, name, price, energy, fat, protein,
                 carbohydrate, gramspermilliliter, gramsperunit):
        """
        Describe an ingredient

        Keyword arguments

        name -- the canonical name of the ingredient

        price -- the current price for the ingredient

        energy -- the amount of energy (in kcal)

        fat -- the amount of fat in grammes per 100g

        protein -- the amount of protein in grammes per 100g

        carbohydrate -- the amount of carbohydrates in grammes per 100g

        gramspermilliliter -- the number of grammes one ml of the
        ingredient weighs

        gramsperunit -- the weight in grammes of one standard unit
        (e.g. one can of tomatoes, an egg)
        """

        super(Ingredient, self).__init__()

        self.name = name
        self.price = price
        self.energy = energy
        self.fat = fat
        self.protein = protein
        self.carbohydrate = carbohydrate
        self.gramspermilliliter = gramspermilliliter
        self.gramsperunit = gramsperunit
        self._id = None

    def save(self):
        if self._id is None:
            query = """INSERT INTO Ingredient (Name, Price, Energy, Fat, Protein,
            Carbohydrate, GramsPerMilliliter, GramsPerUnit)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            arglist = (self.name, self.price, self.energy, self.fat,
                       self.protein, self.carbohydrate,
                       self.gramspermilliliter, self.gramsperunit)
            self._id = self.execute_one(query, arglist)

    @classmethod
    def by_id(cls, _id):
        query = """SELECT * FROM Ingredient WHERE ID = %s"""
        with MySQLdb.connect(**dbconf) as cursor:
            cursor.execute(query, [_id])
            ingredient = cursor.fetchone()

        if ingredient is None:
            raise NotFoundException

        strip_id = ingredient[1:]
        ing = cls(*strip_id)
        ing._id = ingredient[0]
        return ing

    def __str__(self):
        s = ("%s %d") % (self.name, int(self._id))
        return s

    def delete(self):
        """FIXME! briefly describe function

        :returns:
        :rtype:

        """
        query = "DELETE FROM Ingredient WHERE ID = %s"
        arglist = [self._id]
        try:
            self.execute_one(query, arglist)
        except IntegrityError:
            raise IngredientInUseException()

    def refresh(self):
        pass

CookBookObject.register(Ingredient)


class Recipe(CookBookObject):
    def __init__(self, title, cook_time_prep, cook_time_cook,
                 servings, description, version, ingredient_lists,
                 author, instructions, comments, pictures, id=None):
        """
        Describe a recipe

        Keyword arguments

        title -- the title of the recipe

        cook_time_prep -- the time for preparing the recipe in minutes

        cook_time_cook -- the time for cooking the recipe in minutes

        servings -- the estimated number of servings

        description -- a brief description of the recipe

        version -- the version of the recipe

        ingredient_lists -- the list of ingredient lists

        author -- the author of the recipe

        instructions -- the list of instructions for the recipe

        comments -- the list of comments of the recipe

        pictures -- a list of pictures of the recipe


        Examples:

        .. code-block:: python
           :dedent: 1

            bread = Recipe(
            title="bread", servings=4,
            cook_time_prep=30,
            cook_time_cook=30,
            ingredients=[{'title': '',
                          'ingredients': [{'unit': Unit.DL, 'quantity': 17,
                                          'ingredient': Ingredient.from_name("wheat flour")}]}],
            author=Author("Albin Stjerna"),
            instructions=["Blanda mjöl", "sätt på ugnen", "klart!"]
            )

        """

        super(Recipe, self).__init__()

        self.title = title
        self.cook_time_prep = cook_time_prep
        self.cook_time_cook = cook_time_cook
        self.servings = servings
        self.description = description
        self.version = version
        self._id = id

        self.ingredient_lists = ingredient_lists

        self.author = author
        self.instructions = instructions
        self.comments = comments
        self.pictures = pictures

    def save(self):
        if self._id is None:
            query = """INSERT INTO Recipe (Title, CookingTimePrepMinutes,
            CookingTimeCookMinutes, Servings, Description, Version)
            VALUES (%s, %s, %s, %s, %s, %s)"""
            arglist = (self.title, self.cook_time_prep, self.cook_time_cook,
                       self.servings, self.description, self.version)

            self._id = self.execute_one(query, arglist)

            # Link ingredient lists to this recipe
            for ing_list in self.ingredient_lists:
                ing_list.link_to_recipe(self)

            # TODO: Save children to db

    def __str__(self):
        s = ("%s %d") % (self.title, int(self._id))
        return s

    @classmethod
    def by_id(cls, _id):
        recipe_query = """SELECT *
        FROM Recipe WHERE ID = %s"""

        ingredient_list_query = """SELECT IL.ID FROM IngredientList as IL join
         Recipe as R on RecipeID = R.ID WHERE R.ID = %s"""

        instruction_query = """SELECT InstructionID
        FROM Recipe_Instruction join Recipe on RecipeID = Recipe.ID
        WHERE Recipe.ID = %s"""

        with MySQLdb.connect(**dbconf) as cursor:
            # Fetch from Recipe table, strip off ID
            cursor.execute(recipe_query, [_id])
            result = cursor.fetchone()

            if result is None:
                raise NotFoundException

            recipe = result[1:]

            # Fetch ID:s of ingredient lists
            cursor.execute(ingredient_list_query, [_id])
            ingredient_lists_ids = cursor.fetchone()

            # Fetch ID:s of instructions
            cursor.execute(instruction_query, [_id])
            instructions_ids = cursor.fetchone()

        ingredient_lists = {IngredientList.by_id(x) for x in
                            ingredient_lists_ids}

        # TBI
        author = None
        instructions = None
        comments = None
        pictures = None

        return cls(*recipe, ingredient_lists=ingredient_lists, author=author,
                   instructions=instructions, comments=comments,
                   pictures=pictures, id=_id)

    def delete(self):
        query = "DELETE FROM Ingredient WHERE ID = %s"
        arglist = [self._id]
        try:
            self.execute_one(query, arglist)
        except IntegrityError:
            raise IngredientInUseException()

    def refresh(self):
        print("refresh not implemented yet")

CookBookObject.register(Recipe)


class IngredientList(CookBookObject):

    def __init__(self, ingredients, title, _id=None):
        """
        Describe an ingredient list

        Keyword arguments

        ingredients -- the list of ingredients

        title -- the title of the ingredient list

        """

        super(IngredientList, self).__init__()
        self.ingredients = ingredients
        self.title = title
        self._id = _id
        self.recipe_id = None

    def save(self):
        assert(self.recipe_id is not None)
        
        if self._id is None:
            insert_query = """INSERT INTO IngredientList (Title, RecipeID)
            VALUES (%s, %s) """

            self._id = self.execute_one(insert_query, [self.title, self.recipe_id])

            for ingredient in self.ingredients:
                query = """INSERT INTO IngredientList_Ingredient
                      (IngredientListID, IngredientID, PrepNotes,
                       Magnitude, Unit)
                       VALUES(%s, %s, 1, 1, 1)"""

                arglist = [self._id, ingredient._id]
                self.execute_one(query, arglist)
        else:

            update_query = """UPDATE IngredientList 
                       SET (Title, RecipeID) VALUES (%s, %s) """

            self._id = self.execute_one(update_query, [self.title, self.recipe_id])

            for ingredient in self.ingredients:
                query = """UPDATE IngredientList_Ingredient
                      (IngredientListID, IngredientID, PrepNotes,
                       Magnitude, Unit)
                       VALUES(%s, %s, 1, 1, 1)"""

                arglist = [self._id, ingredient._id]

                self.execute_one(query, arglist)
            

    def link_to_recipe(self, recipe):
        """
        Set recipe_id to the id of recipe
        """
        assert self.recipe_id is None
        self.recipe_id = recipe._id

    def __str__(self):
        s = ("Ingredients: %s\n"
             "%s") % (self.title, "\n".join(
                 [str(x) for x in self.ingredients]))
        return s

    @classmethod
    def by_id(cls, _id):
        ingredients_query = """SELECT IngredientID FROM IngredientList_Ingredient
        WHERE IngredientListID = %s"""

        ingredientlist_query = """SELECT * FROM IngredientList
        WHERE ID = %s"""

        with MySQLdb.connect(**dbconf) as cursor:
            # Fetch list of ingredients
            cursor.execute(ingredients_query, [_id])
            ingredient_ids = cursor.fetchone()

            # Fetch title and recipe ID
            cursor.execute(ingredientlist_query, [_id])
            ingredient_list = cursor.fetchone()[1:]

        ingredients = {Ingredient.by_id(ingr_id, dbconf)
                       for ingr_id in ingredient_ids}
        return cls(ingredients, *ingredient_list)

    def refresh(self):
        print("refresh is not implemented yet")

    def delete(self):
        print("delete is not implemented yet")
        
CookBookObject.register(IngredientList)


class IngredientInUseException(Exception):
    pass


class NotFoundException(Exception):
    pass
