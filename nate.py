import turtle


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


def drawthing():
    square = Polygon(4,"Square")
    pentagon = Polygon(5,"Pentagon")

    print(square.sides)
    print(square.name)
    print(pentagon.interior_angles)
    print(pentagon.angle)

    pentagon.draw()



def listhelp():
    lst = [{'asset': 'BTC', 'free': '0.00000062', 'locked': '0.00000000'}]
    newlst = []
    for d in lst:
        if float(d['free']) >= 0.01:
            newlst.append([d['asset'],float(d['free'])])
    for el in newlst:
        print(el[0], el[1])


if __name__ == '__main__':
    listhelp()
    drawthing()