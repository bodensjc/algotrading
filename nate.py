import turtle

"""from test_function import greet_user

user = input("What is your username: ")
greet_user(user)"""

class Polygon:
    def __init__(self, sides, name):
        self.sides = sides
        self.name = name
        self.interior_angles = (self.sides-2)*180
        self.angle = 180-self.interior_angles/self.sides

    def draw(self):
        for i in range(self.sides):
            turtle.forward(100)
            turtle.right(self.angle)
        turtle.done()

square = Polygon(4,"Square")
pentagon = Polygon(5,"Pentagon")

print(square.sides)
print(square.name)
print(pentagon.interior_angles)
print(pentagon.angle)

pentagon.draw()