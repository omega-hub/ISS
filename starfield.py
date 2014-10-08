import csv
from cyclops import *
from omega import *
from euclid import *
from math import *

# set up the geometry shader inputs and outputs, and add the program to the
# scene manager
spriteProgram = ProgramAsset()
spriteProgram.geometryOutVertices = 4
spriteProgram.name = "starfieldProgram"
spriteProgram.geometryInput = PrimitiveType.Points
spriteProgram.geometryOutput = PrimitiveType.TriangleStrip
spriteProgram.vertexShaderName = "ISS/star.vert"
spriteProgram.fragmentShaderName = "ISS/star.frag"
spriteProgram.geometryShaderName = "ISS/star.geom"
getSceneManager().addProgram(spriteProgram)

def loadStars(earth, sfname):
    starMag = float(0)
    starX = float(0)
    starY = float(0)
    starZ = float(0)

    sfmodel = ModelGeometry.create("starfield")
    sfmodel.addVertex(Vector3(0, 0, 0))
    getSceneManager().addModel(sfmodel)
    i = 0
    # for now lets start with 4000 stars in the data file
    with open(sfname,"rU") as data:
        rows = csv.reader(data)
        for row in rows:
            starMag = float(row[0])
            starX = float(row[1])
            starY = float(row[2])
            starZ = float(row[3])

            # convert x, y, z stars so all stars at distance 100000 away in sphere
            distance = sqrt(starX * starX + starY * starY + starZ * starZ)
            starX = starX / distance * 100000
            starY = starY / distance * 100000
            starZ = starZ / distance * 100000

            #print starMag, starX, starY, starZ
            # convert star magnitude to object size
#            refinedScale = (25 - (starMag + 1.5)) * 3
            refinedScale = (25 - (starMag + 1.5))
            refinedScale = refinedScale * refinedScale * refinedScale / 50

            if refinedScale < 1: # < 1
                refinedScale = 1 # 1

            sfmodel.addVertex(Vector3(starX, starY, starZ))
            sfmodel.addColor(Color(1, 1, 1, refinedScale)) # color doesnt matter
            i = i + 1

    # add single primitive batch containing all the stars.
    sfmodel.addPrimitive(PrimitiveType.Points, 0, i)

    # create model
    stars = StaticObject.create("starfield")
    stars.setScale(Vector3(10000, 10000, 10000))
    stars.setEffect('starfieldProgram -t -a')
    earth.addChild(stars)
    stars.setVisible(True)
