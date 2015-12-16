class Person:

    def __init__(self):
        self.pets = []

    def add_pet(self, pet):
        self.pets.append(pet)

jane = Person()
bob = Person()

jane.add_pet("cat")
jane.add_pet("zebra")
bob.add_pet("elephant")
print(jane.pets)
print(bob.pets)
