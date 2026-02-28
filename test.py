class Person: 
    name = "hello"
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_name):
        self._name = new_name


    

mani = Person("Mani")
mani.name = "Sneha"
print(mani.name)


