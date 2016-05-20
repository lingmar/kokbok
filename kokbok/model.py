import MySQLdb
from kokbok import conf

class Ingredient:
    def __init__(self, name, price, energy, fat, protein,
                 carbohydrate, gramspermilliliter, gramsperunit, _id=None):
        self.name = name
        self.price = price
        self.energy = energy
        self.fat = fat
        self.protein = protein
        self.carbohydrate = carbohydrate
        self.gramspermilliliter = gramspermilliliter
        self.gramsperunit = gramsperunit
        self._id = _id

     def save(self):
        if self._id == None:
            query = """INSERT INTO Ingredient (Name, Price, Energy, Fat, Protein,
            Carbohydrate, GramsPerMilliliter, GramsPerUnit)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            arglist = (self.name, self.price, self.energy, self.fat, self.protein,
                        self.carbohydrate, self.gramspermilliliter, self.gramsperunit)
            print(execute_one(query, arglist))

class Recipe:
    def __init__(self, title, cook_time_prep, cook_time_cook, dimension, description, version, _id = None):
        self.title = title
        self.cook_time_prep = cook_time_prep
        self.cook_time_cook = cook_time_cook
        self.dimension = dimension
        self.description = description
        self.version = version
        self._id = _id

    def save(self):
        if self._id == None:
            query = """INSERT INTO Recipe (Title, CookingTimePrepMinutes,
            CookingTimeCookMinutes, Dimension, Description, Description,
            Version)
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            arglist = (self.title, self.cook_time_prep, self.cook_time_cook,
                       dimension, description, version)
            print(execute_one(query, arglist))
            
tdef execute_one(query, arglist):
    with MySQLdb.connect(**conf.db) as cursor:
        cursor.execute(query, arglist)
        return cursor.fetchall()

def execute_many(query, arglist):
    with MySQLdb.connect(**conf.db) as cursor:
        cursor.execute_many(query, arglist)
        return cursor.fetchall()
