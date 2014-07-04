# full scale osgEarth and ISS in orbit demo
# copyright 2013 evl
#
# v 0.0 basic iss model plug rotating earth with static texture
# v 0.1 added atmosphere
# v 0.2 now positioning iss correctly over the planet
# v 0.3 added in 4000 stars, added in shuttle, reoriented station over planet
#       tweaked the shader to work on the mac (added some .0s)

# future enhancements
# - convert spherical stars to shader based stars with correct color / magnitude

from math import *
from euclid import *
from omega import *
from cyclops import *
from omegaToolkit import *
import time

# used to grab iss position data from the web
import urllib2
import json

# used to thread the call to get iss position data from the web
import threading

# fore reading in the stars
import starfield

scene = getSceneManager()
cam = getDefaultCamera()

#cam.setPosition(Vector3(10, 0, 60))

# New default position with Earth below the CAVE
# and a more 'traditional' view of the ISS
# - Arthur 11/18/2013
#cam.setPosition(Vector3(-1.33, -88.24, 21.16))
#cam.setPitchYawRoll(Vector3(1.33,0.0,0.02))

# Initial position version 2
# More Earth, cooler ISS angle, shuttle visible
# by walking forward
# - Arthur 3/10/2014
cam.setPosition(Vector3(-9.5,-134.97,93.59))
cam.setPitchYawRoll(Vector3(1.0,-0.2,0.0))

#set the background to black

scene.setBackgroundColor(Color(0, 0, 0, 1))

#set the far clipping plane back realy far for big objects
#eventually including the Earth

setNearFarZ(1, 100000000)
               
queueCommand(":depthpart on 1000")

progress = None
shuttle = None

lastLat = 0
lastLon = 0
isslat = 0
isslon = 0

oldT = 0

# mi = ModelInfo()
# mi.name = "defaultSphere"
# mi.path = "sphere.obj"
# scene.loadModel(mi)

def onShuttleLoaded():
	global shuttle
	shuttle = StaticObject.create("shuttle")
	shuttle.setPosition(Vector3(-20.0, 5.0, 70.0))
	shuttle.setScale(Vector3(1, 1, 1))

	shuttle.getMaterial().setDoubleFace(0)
	shuttle.getMaterial().setProgram("textured")
	shuttle.getMaterial().setGloss(0)
	shuttle.getMaterial().setShininess(10)

	shuttle.yaw(radians(90.0))
	shuttle.roll(radians(-90.0))

##################################################
# Setup soundtrack 
se = getSoundEnvironment()
se = None
if (se != None):
	print("Setup up music")
	music = se.loadSoundFromFile('moon', 'data/moon.wav')
	time.sleep(1)
	simusic = SoundInstance(music)
	simusic.setPosition(Vector3(0, 2, -1))
	simusic.setLoop(True)
	simusic.setVolume(0.2)
	simusic.playStereo()
    
# end sound

##################################################

# Load an astronaut
# eventually move him around some
# maybe replace him with the Mike avatar
emuModel = ModelInfo()
emuModel.name = "emu"
emuModel.path = "data/NASA-MMU-anim.fbx"
emuModel.optimize = False
scene.loadModel(emuModel)

emu = AnimatedObject.create("emu")
emu.loopAnimation(0)
emu.setPosition(Vector3(14, 0, -10))
emu.setScale(Vector3(0.01, 0.01, 0.01)) # need to check this
emu.getMaterial().setDoubleFace(1) # need inside of helmet to be solid
emu.getMaterial().setProgram("textured")
emu.getMaterial().setGloss(0)
emu.getMaterial().setShininess(10)

##################################################

# create osg Earth
# set ISS at the real ISS loation
#
# earth radius is 6,371 km
# ISS orbits 370 km above the earth
earthModel = ModelInfo()
earthModel.name = "earth"
earthModel.path = "mapquestaerial.earth"
scene.loadModel(earthModel)
earth = StaticObject.create("earth")
earth.getMaterial().setLit(False)

earth.setScale(Vector3(1, 1, 1))

earth.setPosition(Vector3(0, 0, -6900000))
earth.pitch(radians(-70.0))

atmo = SphereShape.create(6371000 + 80000, 5)
earth.addChild(atmo)
atmo.setEffect('./atmosphere -e #9090f030 -a -t')

# # sphere with texture on the inside for background stars
# # kind of low rez, but it will do for now
# skyModel = ModelInfo()
# skyModel.name = "sky"
# skyModel.path = "data/sky.obj"
# skyModel.optimize = False
# scene.loadModelAsync(skyModel, 'skyLoaded()')

# def skyLoaded():
    # sky = StaticObject.create("sky")
    # sky.setPosition(Vector3(0, 0, 0))
    # sky.getMaterial().setDoubleFace(1)
    # sky.setScale(Vector3(1000000000, 1000000000, 1000000000))
    # earth.addChild(sky)

starfield.loadStars(earth, "data/hyparcusxyz_all.csv")
    
##################################################

# Create a directional light
light1 = Light.create()
light1.setLightType(LightType.Directional)
light1.setLightDirection(Vector3(0.0, 0.4, 0.3))
light1.setPosition(light1.getLightDirection() * -100)
light1.setColor(Color(0.2, 0.2, 0.4, 1.0))
light1.setAmbient(Color(0.1, 0.1, 0.15, 1.0))
light1.setSpotCutoff(60)
sm1 = ShadowMap()
sm1.setSoft(True)
sm1.setTextureSize(4096, 4096)
light1.setShadow(sm1)
light1.setShadowRefreshMode(ShadowRefreshMode.Manual)

# Create another directional light
light2 = Light.create()
light2.setLightType(LightType.Directional)
light2.setLightDirection(Vector3(0.0, -0.4, -0.3))
light2.setPosition(light2.getLightDirection() * -100)
light2.setColor(Color(0.25, 0.25, 0.2, 1.0))
light2.setSpotCutoff(60)
sm2 = ShadowMap()
sm2.setSoft(True)
sm2.setTextureSize(4096, 4096)
light2.setShadow(sm2)
light2.setShadowRefreshMode(ShadowRefreshMode.Manual)

# Create a camera mounted light
light3 = Light.create()
light3.setPosition(0,0,0)
light3.setLightDirection(Vector3(0,0,-1))
light3.setColor(Color(1, 1, 1, 1.0))
light3.setAttenuation(0, 0.1, 0.01)
light3.setLightType(LightType.Spot)
light3.setSpotCutoff(50)
light3.setSpotExponent(30)
sm3 = ShadowMap()
sm3.setSoft(True)
sm3.setTextureSize(2048, 2048)
light3.setShadow(sm3)

# Attach light to wand
light3.followTrackable(1)


getDefaultCamera().addChild(light3)
getDefaultCamera().getController().setSpeed(5.0)

#cl = scene.getCompositingLayer()
#cl.loadCompositor('cyclops/common/compositor/hdr.xml')

def onStationLoaded():
    global progress
    progress = StaticObject.create("progress")
    progress.setPosition(Vector3(-4.0, 2.0, -10.0))
    progress.setScale(Vector3(0.254, 0.254, 0.254))

    progress.getMaterial().setDoubleFace(1)
    progress.getMaterial().setProgram("textured")
    progress.getMaterial().setGloss(1)
    progress.getMaterial().setShininess(10)

    # need to get ISS in the correct orientation
    progress.yaw(radians(90.0))
    progress.roll(radians(90.0))
    
    # refresh shadow maps
    sm1.setDirty()
    sm2.setDirty()
#loadStars()

##################################################

# load in ISS
progressModel = ModelInfo()
progressModel.name = "progress"
progressModel.path = "data/ISS.fbx"
progressModel.generateNormals = True
scene.loadModelAsync(progressModel, "onStationLoaded()")

# load in space shuttle
shuttleModel = ModelInfo()
shuttleModel.name = "shuttle"
shuttleModel.path = "data/ss.fbx"
shuttleModel.generateNormals = True
scene.loadModelAsync(shuttleModel, "onShuttleLoaded()")

# slave nodes update their earth rotation based on data from the master
def newISSData(newlat, newlon):
	global isslat
	global isslon

	isslat = newlat
	isslon = newlon

# master grabs data from the web every 5 seconds and sends it to the rest of the nodes
# based on script from http://open-notify.org/Open-Notify-API/ISS-Location-Now
def positionUpdate():
    global isslat
    global isslon

    if isMaster():
#	    print "I AM THE MASTER"

	    req = urllib2.Request("http://api.open-notify.org/iss-now.json")
	    response = urllib2.urlopen(req)

	    obj = json.loads(response.read())

#	    print obj['iss_position']['latitude'], obj['iss_position']['longitude']

	    isslat = obj['iss_position']['latitude']
	    isslon = obj['iss_position']['longitude']

	    broadcastCommand('newISSData(' + str(isslat) + ',' + str(isslon) + ')')

	    # thread should trigger every 5 seconds - seems like a lot longer right now
	    #print "restarting the timer thread"
	    #issPositionThread = threading.Timer(5.0, positionUpdate)
	    #issPositionThread.start()

# Spin the earth slowly
def onUpdate(frame, t, dt):

# originally just spinning the earth
#    earth.roll(dt/200)

    global lastLat
    global lastLon
    global isslat
    global isslon

    global oldT

    # reset the earth rotation to the equator S of Greenwich
    earth.setOrientation(Quaternion())
    earth.pitch(radians(-90))
    earth.roll(radians(-90))

    # now rotate the earth to keep the ISS in the right place above it
    # doing interpolation to smooth out the movement (should reate to dt in future)
    # if we havent had data in a while then update to recent data without interpolation

    if (t - oldT) > 5:
	    positionUpdate()
	    oldT = t

    if fabs(isslat - lastLat) > 5.0:
	    issYaw = isslat
    else:
	    issYaw = (isslat*0.001 + lastLat*0.999)

    if fabs(isslon - lastLon) > 5.0:
	    issRoll = isslon
    else:
	    issRoll = (isslon*0.001 + lastLon*0.999)

    earth.yaw(radians(issYaw))  
    earth.roll(radians(-issRoll)) 
		    
    lastLat = issYaw
    lastLon = issRoll

setUpdateFunction(onUpdate)

# update the position of the space station
#positionUpdate()

def handleEvent():
    global earth
    #global s_sound

    e = getEvent()
    if(e.isButtonDown(EventFlags.ButtonLeft)):
        print("Left button pressed")
	earth.setScale(                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        Vector3(0.5, 0.5, 0.5))

        #play button sound                                                           
        # si_sound = SoundInstance(s_sound)
        # si_sound.setPosition( e.getPosition() )
        # si_sound.setVolume(1.0)
        # si_sound.setWidth(20)
        # si_sound.play()

    if(e.isButtonDown(EventFlags.ButtonRight)):
        print("Right button pressed")
	earth.setScale(Vector3(1, 1, 1))

        #play button sound                                                           
	# si_sound = SoundInstance(s_sound)
        # si_sound.setPosition( e.getPosition() )
        # si_sound.setVolume(1.0)
        # si_sound.setWidth(20)
        # si_sound.play()

setEventFunction(handleEvent)
