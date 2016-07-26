import MySQLdb
from _mysql_exceptions import IntegrityError

from kokbok import conf

from abc import ABCMeta, abstractmethod


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
    def by_id(self):
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

    def execute_one(self, query, arglist, dbconf=None):
        if not dbconf:
            dbconf = self.dbconf
        with MySQLdb.connect(**dbconf) as cursor:
            cursor.execute(query, arglist)

            cursor.execute("SELECT LAST_INSERT_ID()")
            return cursor.fetchone()[0]

    def execute_many(self, query, arglist, dbconf=None):
        if not dbconf:
            dbconf = self.dbconf
        with MySQLdb.connect(**dbconf) as cursor:
            cursor.execute_many(query, arglist)
            return cursor.fetchone()

    def __init__(self, dbconf):
        """
        dbconf -- the expected configuration for MySQLdb.connect.
        Probably conf.db.
        """
        self.dbconf = dbconf


class Ingredient(CookBookObject):

    def __init__(self, name, price, energy, fat, protein,
                 carbohydrate, gramspermilliliter, gramsperunit,
                 dbconf=conf.db):
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

        super(Ingredient, self).__init__(dbconf)

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
        with MySQLdb.connect(**conf.db) as cursor:
            cursor.execute(query, [_id])
            ingredient = cursor.fetchone()
        strip_id = ingredient[1:]
        ing = cls(*strip_id)
        ing._id = ingredient[0]
        return ing

    def __str__(self):
        s = ("%s %d") % (self.name, int(self._id))
        return s

    def delete(self):
        query = "DELETE FROM Ingredient WHERE ID = %s"
        arglist = [self._id]
        try:
            self.execute_one(query, arglist)
        except IntegrityError:
            raise IngredientInUseException()

    def refresh(self):
        pass

CookBookObject.register(Ingredient)


class Recipe():
    def __init__(self, title, cook_time_prep, cook_time_cook,
                 servings, description, version, ingredient_lists,
                 author, instructions, comments, pictures, id=None,
                 dbconf=conf.db):
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

        """

        super(Recipe, self).__init__(dbconf)

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

    def __str__(self):
        s = ("%s %d") % (self.title, int(self._id))
        return s

    def delete(self):
        query = "DELETE FROM Ingredient WHERE ID = %s"
        arglist = [self._id]
        try:
            self.execute_one(query, arglist)
        except IntegrityError:
            raise IngredientInUseException()

CookBookObject.register(Recipe)


class IngredientList:

    def __init__(self, ingredients, title, _id=None, dbconf=conf.db):
        """
        Describe an ingredient list

        Keyword arguments

        ingredients -- the list of ingredients

        title -- the title of the ingredient list

        """

        super(IngredientList, self).__init__(dbconf)
        self.ingredients = ingredients
        self.title = title
        self._id = _id

    def save(self):
        if self._id is None:
            query = """INSERT INTO IngredientList (Title)
            VALUES (%s) """

            self._id = self.execute_one(query, [self.title])

            for ingredient in self.ingredients:
                query = """INSERT INTO IngredientList_Ingredient
                      (IngredientListID, IngredientID, PrepNotes,
                       Magnitude, Unit)
                       VALUES(%s, %s, 1, 1, 1)"""

                arglist = [self._id, ingredient._id]

                self.execute_one(query, arglist)

    def __str__(self):
        s = ("Ingredients: %s\n"
             "%s") % (self.title, "\n".join(
                 [str(x) for x in self.ingredients]))
        return s


CookBookObject.register(IngredientList)


class IngredientInUseException(Exception):
    pass
