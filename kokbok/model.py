import MySQLdb

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

        gramspermilliliter -- the number of grammes one ml of the ingredient weighs

        gramsperunit -- the weight in grammes of one standard unit (e.g. one can of tomatoes, an egg)
    """

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
        if self._id == None:
            query = """INSERT INTO Ingredient (Name, Price, Energy, Fat, Protein,
            Carbohydrate, GramsPerMilliliter, GramsPerUnit)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            arglist = (self.name, self.price, self.energy, self.fat, self.protein,
                        self.carbohydrate, self.gramspermilliliter, self.gramsperunit)
            self._id = execute_one(query, arglist)

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
        pass

    def refresh(self):
        pass


class Recipe():
    def __init__(self, title, cook_time_prep, cook_time_cook,
                 dimension, description, version, ingredient_lists,
                 author, instruction, comments, pictures, _id = None):

        self.title = title
        self.cook_time_prep = cook_time_prep
        self.cook_time_cook = cook_time_cook
        self.dimension = dimension
        self.description = description
        self.version = version
        self._id = _id

        self.ingredient_lists = ingredient_lists

        self.author = author
        self.instruction = instruction
        self.comments = comments
        self.pictures = pictures

    def save(self):
        if self._id == None:
            query = """INSERT INTO Recipe (Title, CookingTimePrepMinutes,
            CookingTimeCookMinutes, Dimension, Description, Version)
            VALUES (%s, %s, %s, %s, %s, %s)"""
            arglist = (self.title, self.cook_time_prep, self.cook_time_cook,
                       self.dimension, self.description, self.version)

            self._id = execute_one(query, arglist)


class IngredientList:

    def __init__(self, ingredients, title, _id=None):
        self.ingredients = ingredients
        self.title = title
        self._id = _id

    def save(self):
        if self._id == None:
            query = """INSERT INTO IngredientList (Title)
            VALUES (%s) """

            self._id = execute_one(query, [self.title])

            for ingredient in self.ingredients:
                query = """INSERT INTO IngredientList_Ingredient
                      (IngredientListID, IngredientID, PrepNotes,
                       Magnitude, Unit)
                       VALUES(%s, %s, 1, 1, 1)"""

                arglist = [self._id, ingredient._id]

                execute_one(query, arglist)

    def __str__(self):
        s = ("Ingredients: %s\n"
             "%s") % (self.title, str(self.ingredients))

        return s


def execute_one(query, arglist):
    with MySQLdb.connect(**conf.db) as cursor:
        cursor.execute(query, arglist)

        cursor.execute("SELECT LAST_INSERT_ID()")
        return cursor.fetchone()[0]

def execute_many(query, arglist):
    with MySQLdb.connect(**conf.db) as cursor:
        cursor.execute_many(query, arglist)
        return cursor.fetchone()
