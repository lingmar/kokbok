import MySQLdb
from _mysql_exceptions import IntegrityError, MySQLError

from abc import ABCMeta, abstractmethod

import kokbok.conf


global dbconf
dbconf = kokbok.conf.get_db_conf()


class Unit():
    """
    Represents available unit measurements (for ingredient
    lists). Available options are:
    - ML (millilitres)
    - G (grammes)
    - PCS (pieces)
    """

    ML = "ml"
    G = "g"
    PCS = "pcs"


def db_init():
    """
    Initialise a new (clean) database.
    """
    conf_no_db_name = dbconf.copy()
    conf_no_db_name.pop('db')

    with MySQLdb.connect(**conf_no_db_name) as cursor:
        with open('kokbok.sql') as x:
            for line_no, line in enumerate(x.read().split(';\n')):
                if len(line.strip()) > 0:
                    try:
                        cursor.execute(line % {'dbname': dbconf['db']})
                    except MySQLError as e:
                        print(("Error executing command number %(lineno)d: "
                               "%(line)s. Error was: %(error)s")
                              % {'line': line.strip(),
                                 'lineno': line_no,
                                 'error': str(e)})
                        raise e


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

    __repr__ = __str__

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

    def __eq__(self, other):
        return isinstance(other, Ingredient) and self._id == other._id

    def __ne__(self, other):
        return not self.__eq(other)


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

    @classmethod
    def new(_class, title, servings, cook_time_prep, cook_time_cook, ingredients,
            author, instructions, description, version):
        """"
        Create a new recipe and save it to database.

        Examples:

        .. code-block:: python
           :dedent: 1

            bread = Recipe.new(
            title="bread",
            servings=4,
            cook_time_prep=30,
            cook_time_cook=30,
            ingredients=[{'title': '',
                          'ingredients': [{'unit': Unit.ML, 'quantity': 17, 'prepnotes': None,
                                          'ingredient': Ingredient.from_name("wheat flour")}]}],
            author=Author.from_name("Albin Stjerna"),
            instructions=["Blanda mjöl", "sätt på ugnen", "klart!"]
            description="Jättegott bröd"
            version=1
            )
        """
        ingredient_lists = [IngredientList(**x) for x in ingredients]

        recipe = Recipe(title=title, cook_time_prep=cook_time_prep,
                        cook_time_cook=cook_time_cook, servings=servings,
                        description=description, version=version,
                        ingredient_lists=ingredient_lists, author=author,
                        instructions=instructions, pictures=None, comments=None)
        recipe.save()
        return recipe

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
                ing_list.save()

            instruction_query = """INSERT INTO Instruction (Text)
            VALUES (%s)"""
            recipe_instruction_query = """INSERT INTO Recipe_Instruction
            (RecipeID, InstructionID, Step) VALUES (%s, %s, %s)"""

            for step, instruction in enumerate(self.instructions, start=1):
                instruction_id = self.execute_one(instruction_query, [instruction])

                self.execute_one(recipe_instruction_query,
                                 (self._id, instruction_id, step))

            if self.author:
                author_id = self.author_id(self.author)
                if not author_id:
                    author_id = self.execute_one(("INSERT INTO Author (Name)"
                                                  " VALUES (%s)"),
                                                 [self.author])
                self.execute_one(("INSERT INTO Author_Recipe "
                                  "(AuthorID, RecipeID) VALUES (%s, %s)"),
                                  [author_id, self._id])

    def author_id(self, author):
        query = "SELECT ID from Author WHERE Name = %s"
        with MySQLdb.connect(**dbconf) as cursor:
            cursor.execute(query, [author])
            result = cursor.fetchone()
            return result[0] if result else result
            
    def __str__(self):
        s = ("%s %d") % (self.title, int(self._id))
        return s

    __repr__ = __str__


    @classmethod
    def by_id(cls, _id):

        recipe_query = """SELECT *
        FROM Recipe WHERE ID = %s"""

        ingredient_lists = IngredientList.from_recipe_id(_id)

        # FIXME: Instruction class?
        instruction_query = """SELECT Text
        FROM Instruction join Recipe_Instruction
        ON Instruction.ID = Recipe_Instruction.InstructionID
        WHERE Recipe_Instruction.RecipeID = %s
        ORDER BY Step ASC"""

        author_query = """SELECT Name
        FROM Author join Author_Recipe
        ON Author.ID = Author_Recipe.AuthorID
        WHERE Author_Recipe.RecipeID = %s"""

        with MySQLdb.connect(**dbconf) as cursor:
            # Fetch from Recipe table, strip off ID
            cursor.execute(recipe_query, [_id])
            result = cursor.fetchone()

            if result is None:
                raise NotFoundException

            # Fetch instructions
            cursor.execute(instruction_query, [_id])
            instructions = [i for (i,) in cursor.fetchall()]

            cursor.execute(author_query, [_id])
            ret_author = cursor.fetchone()
            author = ret_author[0] if ret_author else ret_author
            
            recipe = result[1:]
            
        # TBI
        #instructions = Instruction.from_recipe_id(_id)

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

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            selfdict = self.__dict__.copy()
            otherdict = other.__dict__.copy()

            # Don't compare IDs:
            selfdict.pop("_id")
            otherdict.pop("_id")

            ingredient_lists1 = selfdict.pop('ingredient_lists')
            ingredient_lists2 = otherdict.pop('ingredient_lists')

            same_lists = all((l1 == l2 for (l1, l2) in zip(ingredient_lists1, ingredient_lists2)))

            # for il1, il2 in zip(ingredient_lists1, ingredient_lists2):
            #     if not il1 == il2:
            #         print("{il1} != {il2}".format(il1=il1, il2=il2))

            return selfdict == otherdict and same_lists

    def __ne__(self, other):
        return not self.__eq__(other)

CookBookObject.register(Recipe)


class IngredientList(CookBookObject):

    def __init__(self, title, ingredients, _id=None):
        """
        Describe an ingredient list

        Keyword arguments

        title -- the title of the ingredient list

        ingredients -- the list of ingredients, for example: [{'unit': Unit.ML,
        'quantity': 17, 'prepnotes': None,
        'ingredient': Ingredient.from_name("wheat flour")}]

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
                coupling_query = """INSERT INTO IngredientList_Ingredient
                      (IngredientListID, IngredientID, PrepNotes,
                       Magnitude, Unit)
                       VALUES(%s, %s, %s, %s, %s)"""

                arglist = [self._id, ingredient['ingredient']._id,
                           ingredient['prepnotes'], ingredient['quantity'],
                           ingredient['unit']]
                self.execute_one(coupling_query, arglist)

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

    __repr__ = __str__


    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        same_titles = self.title == other.title

        same_ingredients = self.ingredients == other.ingredients

        return same_titles and same_ingredients

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def by_id(cls, _id):
        ingredients_query = """SELECT IngredientID, PrepNotes, Magnitude, Unit
        FROM IngredientList_Ingredient
        WHERE IngredientListID = %s"""

        ingredientlist_query = """SELECT ID, Title, RecipeID FROM IngredientList
        WHERE ID = %s"""

        with MySQLdb.connect(**dbconf) as cursor:
            # Fetch list of ingredients
            cursor.execute(ingredients_query, [_id])
            ingredient_data = cursor.fetchall()

            # Fetch title and recipe ID
            cursor.execute(ingredientlist_query, [_id])
            (il_id, il_title, il_recipeID) = cursor.fetchone()

            ingredients = [{"ingredient": Ingredient.by_id(ingr_id),
                            "prepnotes": ingr_prepnotes, "quantity": ingr_quantity,
                            "unit": ingr_unit}
                           for (ingr_id, ingr_prepnotes, ingr_quantity,
                                ingr_unit)
                           in ingredient_data]

        ingredient_list = cls(il_title, ingredients, il_id)
        ingredient_list.recipe_id = il_recipeID

        return ingredient_list

    def refresh(self):
        print("refresh is not implemented yet")

    def delete(self):
        print("delete is not implemented yet")

    @classmethod
    def from_recipe_id(cls, recipe_id):
        """
        Returns the ingredient lists of the recipe with recipe_id
        """
        query = """SELECT IL.ID FROM IngredientList as IL join
         Recipe as R on RecipeID = R.ID WHERE R.ID = %s"""

        with MySQLdb.connect(**dbconf) as cursor:
            # Fetch ID:s of ingredient lists
            cursor.execute(query, [recipe_id])
            ingredient_lists_ids = cursor.fetchone()

            if ingredient_lists_ids is None:
                raise NotFoundException

        ingredient_lists = [IngredientList.by_id(x) for x in
                            ingredient_lists_ids]

#        [print(l.__dict__) for l in ingredient_lists]
        return ingredient_lists


CookBookObject.register(IngredientList)


class IngredientInUseException(Exception):
    pass


class NotFoundException(Exception):
    pass
