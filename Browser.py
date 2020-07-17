import os, fnmatch, sys, configparser, datetime, logging
import xml.etree.ElementTree as ET
import pygame

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_RETURN,
    K_BACKSPACE,
    KEYUP,
    KEYDOWN,
    QUIT,
)

###   Display title for console   ###

print("Welcome to Browser!")

###   Global Variables   ###

#configuration variables - these are variables defined by the user through the browser-config.txt file in the same directory as this program file
romLocations = {} #dictionary for storing the locations of each emulator
iconLocations = {} #dictionary for storing the location(s) of icons
saveInfoBGColor = (0, 0, 0, 200) #color of the background for the info box of each save. Can be set by user through config; this is the default setting
saveInfoBGImage = None #image used for the background of the info box of each save. Can be set by user through config; this is the default
cursorImage = "images/cursor-003.png" #image used for the cursor, defined by user through config; this is the default setting
BGImage = "images/background-001.png" #image used for the BG, defined by user through config; this is the default setting
returnImage = "images/return-001.png" #image used for the return icon, defined by user through config; this is the default setting
defaultEmulatorIcon = "images/default-save-001.png" #the default icon sprite used if an emulator icon doesn't exist
defaultSaveIcon = "images/default-save-001.png" #the default icon sprite used if a game save icon doesn't exist

emulators = {} #dictionary for storing the name of each emulator found - this name matches the folder name
gameSaveFiles = {} #dictionary for storing the game saves of each emulator
gameSaveSprites = [] #array/list for game saves used in the GUI
screenWidth = 1600 #width for pygame
screenHeight = 900 #height for pygame
columnLength = 6 #how many columns for the game save grid
columnPosition = 0 #where the cursor is horiztonally in the save grid
rowPosition = 0 #where the cursor is vertically in the save grid
currentPosition = 0 #Column & Row added together to determine the current position of the cursor in the array/list of gameSaveSprites
currentLevel = "Main Menu" #which level/menu/screen/area/etc of the browser the user is on. Determined by hitting enter
currentSave = None #variable used for the saveFileInfo class that stores numerous variables used to display specific save file info
gameSaves = [] #list used to store multiple variables for each game save loaded
totalHeight = 0 #total height of the rows displayed. A variable is fed into this
allEmulatorSprites = None #variable used for holding a class that has sprites for emulators
allSaveSprites = None #variable used for holding a class that has sprites for game saves
saveInfoList = []
selectedItem = None
gridX = None #top left position of grid x
gridY = None #top left position of grid y
gameFont = None #variable holding the font class for the game
screen = None #variable holding the screen class for the game

###   Functions   ###

def loadEmulators(path): #searches the roms folder to see which emulators are active
    items = os.listdir(path) #array/list of all items in the path
    tempDictionary = {} #temporary dictionary used to record each emulator and it's path
    logging.debug("Loading emulators")
    for i in items: #let's check each item in the directory
        if os.path.isdir(os.path.join(path, i)): #is it a folder/path?
            tempDictionary.update( { i : path + "/" + i}) #if so, add it's name and full path to the temp dictionary
            logging.debug(tempDictionary[i] + " loaded") #debugging info, prints the result
    return tempDictionary #returns the final dictionary with all emulators and their paths added

def findSaves(emulator, path, pattern): #finds the game save file and adds it to the gameSaves dictionary. Pattern = game save file type
    directory = os.listdir(path.rstrip()) #local variable for an array/list of the files in the directory
    tempDictionary = {} #temporary dictionary for the function
    currentList = [] #array/list for storing the game save files during the function
    for file in directory: #for loop to check each file
        if (fnmatch.fnmatch(file, pattern)): #if the file matches the pattern "*.srm", then
            currentList.append(file) #add the game save to the array/list
            tempDictionary.update( {emulator : currentList}) #add file to the gameSaves dictionary
            logging.debug(file + " loaded")
    return tempDictionary #returns the dictionary built in the app

def loadGameSaveSprites(imageLocation, saveFiles, sprite, baseX, baseY, emulator): #This function lays out sprites per game save along a 6 x forever grid. Emulator = specific emulator to load OR "all" which loads all sprites
    global columnLength
    global allSprites
    global gameSaveSprites
    global returnImage
    global defaultSaveIcon
    i = 0 #used to count game saves
    xReset = 0 #used to determine when a new line needs to be created
    totalHeight = 0; #used to count the total number of lines. This variable is returned by the function
    iconx = baseX #x coordinate info for the sprite created
    icony = baseY #y coordinate info for the sprite created
    if emulator == "all":
        for key, value in saveFiles.items(): #For each emulator, create a sprite for each game save
            if key == "default": #if we're on the default icon in the dictionary
                continue
            elif config.has_option('Icons', key) == True:
                saveIcon = imageLocation + "/" + config['Icons'][key]
            else:
                saveIcon = defaultSaveIcon
            if os.path.exists(saveIcon) == False:
                logging.warning(saveIcon + " does not exist! Attempting to use program default icon. There will be another error message if the program default icon fails.")
                saveIcon = defaultSaveIcon
            for save in value: #this loop is to look at each game save in the associate values with the emulator
                iconx = baseX + (128*xReset) #For each iteration, xReset is used to create a sprite exactly one length over from the previous sprite
                if xReset == columnLength and i != 0: #This checks if this is the 7th sprite created. Note, ignores the very first sprite (0)
                    icony += 128 #If it's the 4th sprite, we'll create a new line
                    iconx = baseX #Reset our iconx to zero
                    xReset = 0 #Reset our xReset for this iteration on this line
                    totalHeight += 1 #Counts up on our totalHeight variable so we can return how many lines were created
                tempFile = saveFileInfo()
                tempFile.loadSave(value, save)
                if tempFile.icon != None:
                    saveIcon = tempFile.icon
                sprite.append( Icon(saveIcon, iconx, icony, save, value, True) ) #creates the sprite for the save and stores the name within the Icon class
                allSprites.add(sprite[i]) #adds the specific sprite (indicated by the i variable we used to count where we are) to the allSprites sprite group so pygame can update its location on screen
                i += 1 #increase our counter for each iteration
                xReset +=1 #increase our xReset for each iteration
    else:
        for save in saveFiles[emulator]: #Create a sprite for each game save in the user specified emulator
            if config.has_option('Icons', emulator) == True:
                saveIcon = imageLocation + "/" + config['Icons'][emulator]
            else:
                saveIcon = defaultSaveIcon
            if os.path.exists(saveIcon) == False:
                logging.warning(saveIcon + " does not exist! Attempting to use program default icon. There will be another error message if the program default icon fails.")
                saveIcon = defaultSaveIcon
            iconx = baseX + (128*xReset) #For each iteration, xReset is used to create a sprite exactly one length over from the previous sprite
            if xReset == columnLength and i != 0: #This checks if this is the 7th sprite created. Note, ignores the very first sprite (0)
                icony += 128 #If it's the 4th sprite, we'll create a new line
                iconx = baseX #Reset our iconx to zero
                xReset = 0 #Reset our xReset for this iteration on this line
                totalHeight += 1 #Counts up on our totalHeight variable so we can return how many lines were created
            tempFile = saveFileInfo()
            tempFile.loadSave(emulator, save)
            if tempFile.icon != None:
                saveIcon = tempFile.icon
            sprite.append( Icon(saveIcon, iconx, icony, save, emulator, True) ) #creates the sprite for the emulator and stores the name within the Icon class
            allSprites.add(sprite[i]) #adds the specific sprite (indicated by the i variable we used to count where we are) to the allSprites sprite group so pygame can update its location on screen
            i += 1 #increase our counter for each iteration
            xReset +=1 #increase our xReset for each iteration
        iconx = baseX + (128*xReset)
        if (xReset == columnLength and i != 0):
            icony += 128
            iconx = baseX
            xReset = 0
            totalHeight += 1
        sprite.append( Icon(returnImage, iconx, icony, "return", "return", True) )
        allSprites.add(sprite[i])
    return totalHeight

def loadGameSaveSprite(imageLocation, sprite, baseX, baseY, emulator, saveSpecificIcon):
    if config.has_option('Icons', emulator) == True:
        saveIcon = imageLocation + "/" + config['Icons'][emulator]
    else:
        saveIcon = imageLocatioin = "/" + config['Icons']['default']
    if os.path.exists(saveIcon) == False:
        logging.warning(saveIcon + " does not exist! Attempting to use program default icon. There will be another error message if the program default icon fails.")
        saveIcon = imageLocation + "/" + config['Icons']['default']
    if saveSpecificIcon != None:
        saveIcon = saveSpecificIcon
    sprite.append( Icon(saveIcon, baseX, baseY, None, None, False) )

def loadEmulatorSprites(imageLocation, saveFiles, sprite, baseX, baseY):
    global columnLength
    global allSprites
    i = 0 #used to count game saves
    xReset = 0 #used to determine when a new line needs to be created
    totalHeight = 0; #used to count the total number of lines. This variable is returned by the function
    iconx = baseX #x coordinate info for the sprite created
    icony = baseY #y coordinate info for the sprite created
    for key, value in saveFiles.items(): #For each emulator, create a sprite for each game save
        if key == "default": #if we're on the default icon in the dictionary
            continue
        elif config.has_option('Icons', key) == True:
            saveIcon = imageLocation + "/" + config['Icons'][key]
        else:
            saveIcon = defaultEmulatorIcon
        if os.path.exists(saveIcon) == False:
            logging.warning(saveIcon + " does not exist! Attempting to use program default icon. There will be another error message if the program default icon fails.")
            saveIcon = defaultEmulatorIcon
        iconx = baseX + (128*xReset) #For each iteration, xReset is used to create a sprite exactly one length over from the previous sprite
        if xReset == columnLength and i != 0: #This checks if this is the 7th sprite created. Note, ignores the very first sprite (0)
            icony += 128 #If it's the 4th sprite, we'll create a new line
            iconx = baseX #Reset our iconx to zero
            xReset = 0 #Reset our xReset for this iteration on this line
            totalHeight += 1 #Counts up on our totalHeight variable so we can return how many lines were created
        sprite.append( Icon(saveIcon, iconx, icony, key, None, True) ) #creates the sprite for the emulator and stores the name within the Icon class
        allSprites.add(sprite[i]) #adds the specific sprite (indicated by the i variable we used to count where we are) to the allSprites sprite group so pygame can update its location on screen
        i += 1 #increase our counter for each iteration
        xReset +=1 #increase our xReset for each iteration
    return totalHeight

def resetPosition(sprite):
    global gridX
    global gridY
    global columnPosition
    global rowPosition
    sprite.rect.x = gridX
    sprite.rect.y = gridY
    columnPosition = 0
    rowPosition = 0

class saveFileInfo:
    def __init__(self):
        self.path = None
        self.icon = None
        self.name = "None"
        self.lastPlayed = "No data found"
        self.lastSaved = "No data found"
        self.saveFileLocation = "Error, no save file found"
        self.saveIconLocation = "Error, no icon file found"
        self.xmlFileLocation = None
    
    def loadSave(self, emulator, game):
        #necessary global variables
        global romLocations
        global iconLocations
        global xmlLocation
        
        #local variables
        gamePath = "./" + game #path of the game modified to match the XML of emulation station
        
        self.saveFileLocation = romLocations + "/" + emulator + "/" + game
        self.saveIconLocation = iconLocations + "/" + emulator + "/" + config["Icons"][emulator]
        self.xmlFileLocation = xmlLocation + "/" + emulator + "/gamelist.xml"
        
        found = False #variable used to determine if the game save info was found
        
        try:
            # create element tree object
            tree = ET.parse(self.xmlFileLocation)
            
            # get root element 
            root = tree.getroot()
            
            # iterate news items 
            for item in root.findall('game'): #find all <game> tags in the XML file and check the children of each
                itemPath = item.find('path').text #local variable created for name checking
                if os.path.splitext(itemPath)[0] != os.path.splitext(gamePath)[0]: #[:-4] removes the file type and checks the name of the rom with the save
                    self.name = "Error, no save file found"
                    #print(item.find('path').text) #debug info, prints the mis-matched file
                    found = False
                else: #if the name of the rom matches the name of the save
                    found = True
                if found == True: #If the game save was found
                    self.name = item.find('name').text #set the name of this object
                    if item.find('icon') != None: #does the <icon> tag exist for this game save in the gamelist.xml?
                        self.icon = item.find('icon').text #set the image for the icon of this save
                    if item.find('lastplayed') != None: #does the <lastplayed> tag exist for this game save in the gamelist.xml?
                        self.lastPlayed = item.find('lastplayed').text[4:6] + "/" + item.find('lastplayed').text[6:8] + "/" + item.find('lastplayed').text[0:4] #set the last played text of this save
                    if os.path.exists(self.saveFileLocation):
                        saveDate = os.path.getmtime(self.saveFileLocation)
                        saveDate = datetime.datetime.fromtimestamp(saveDate).strftime('%Y-%m-%dT%H:%M:%S')
                        self.lastSaved = saveDate[5:7] + "/" + saveDate[8:10] + "/" + saveDate[0:4]
                    break #since we found the save, break the loop and end the function
        except Exception as e:
            logging.error("Exception occured:", exc_info=True)

###   Logging   ###
logging.basicConfig(level=logging.DEBUG, filename='Browser-error_log.txt', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug('Browser Error Log Created')
###   Configuration   ###
try:
    config = configparser.ConfigParser() #use configparser to read the config file
    config.read("browser-config.txt") #read the file
    #load file path info into game from config file
    romLocations = config['File Paths']['Roms']
    iconLocations = config['File Paths']['Icons']
    xmlLocation = config['File Paths']['Gamelists']
    defaultEmulatorIcon = config['GUI']['defaultEmulatorIcon'] #the default icon sprite used if an emulator icon doesn't exist
    defaultSaveIcon = config['GUI']['defaultSaveIcon'] #the default icon sprite used if a game save icon doesn't exist
    if config.has_section('GUI'):
        if config.has_option('GUI','saveInfoBGColor'): saveInfoBGColor = tuple(map(int, config['GUI']['saveInfoBGColor'].split(', ')))
        else: logging.warning("saveInfoBGColor is missing from the [GUI] section")
        if config.has_option('GUI','saveInfoBGImage'): saveInfoBGImage = config['GUI']['saveInfoBGImage']
        else: logging.warning("saveInfoBGImage is missing from the [GUI] section")
        if config.has_option('GUI','cursorImage'): cursorImage = config['GUI']['cursorImage']
        else: logging.warning("cursorImage is missing from the [GUI] section")
        if config.has_option('GUI','BGImage'): BGImage = config['GUI']['BGImage']
        else: logging.warning("BGImage is missing from the [GUI] section")
        if config.has_option('GUI','returnImage'): returnImage = config['GUI']['returnImage']
        else: logging.warning("returnImage is missing from the [GUI] section")
        if config.has_option('GUI','defaultEmulatorIcon'): defaultEmulatorIcon = config['GUI']['defaultEmulatorIcon']
        else: logging.warning("defaultEmulatorIcon is missing from the [GUI] section")
        if config.has_option('GUI','defaultSaveIcon'): defaultSaveIcon = config['GUI']['defaultSaveIcon']
        else: logging.warning("defaultSaveIcon is missing from the [GUI] section")
    else:
        logging.warning("browser-config.txt has no [GUI] section")
    logging.debug("Configuration loaded!")
except Exception as e:
    logging.critical("browser-config.txt is missing! Unable to run Browser without this config file because Browser requires paths to game saves, roms, and emulators", exc_info=True)
    sys.exit("Quitting program unexpectdly. Check error_log.txt")
                
logging.debug("loading roms...")

emulators = loadEmulators(romLocations) #Load the emulators

logging.debug("Emulators loaded!") #debug info
logging.debug("Loading game saves in the file format of: .srm ...") #debug info

for key, value in emulators.items(): #load the ".srm" game saves
    gameSaveFiles.update(findSaves(key, value, "*.srm"))

logging.debug("Game saves loaded!") #debug info

#if (input("View game saves?") == "Yes"): #view the results? debug info
#    for key, value in gameSaveFiles.items():
#        print(key, ":", value) #for each key in the gameSaves dictionary, show the value(s)

###   Game   ###

if (1 == 1): #used to be: input("Launch Browser?") == "Yes" for debugging, but changed to 1 == 1 to automatically launch program
    
    ###   Pygame Initilization Steps   ###
    logging.debug("Loading Pygame...")
    pygame.init() #initialize pygame
    logging.debug("Pygame Loaded!")
    
    screen = pygame.display.set_mode([screenWidth, screenHeight]) #set screen size
    gridX = int((screenWidth-columnLength*128)/2) #set grid x position
    gridY = 128 #set grid y position
    
    running = True #establish that the game is running
    
    ###   Define sprite objects   ###
    logging.debug("Defining sprite objects and loading sprites...")
    class Icon(pygame.sprite.Sprite):
        def __init__(self, iconImage, offsetx, offsety, save, emulator, resize):
            super(Icon, self).__init__()
            global gameFont
            global defaultEmulatorIcon
            global defaultSaveIcon
            global returnImage
            self.font = gameFont
            if os.path.exists(iconImage):
                self.image = pygame.image.load(iconImage)
                self.image.set_colorkey((255, 255, 255), RLEACCEL)
            elif os.path.exists(defaultEmulatorIcon) and emulator == None:
                logging.warning(iconImage + " does not exist!")
                self.image = pygame.image.load(defaultEmulatorIcon)
                self.image.set_colorkey((255, 255, 255), RLEACCEL)
            elif os.path.exists(defaultSaveIcon) and emulator != None:
                logging.warning(iconImage + " and " + defaultEmulatorIcon + " does not exist!")
                self.image = pygame.image.load(defaultSaveIcon)
                self.image.set_colorkey((255, 255, 255), RLEACCEL)
            else:
                logging.warning(iconImage + " and " + defaultEmulatorIcon + " and " + defaultSaveIcon + " does not exist!")
                self.image = self.font.render("Image File(s) Missing!", True, (255, 255, 255))
            self.rect = self.image.get_rect()
            self.size = self.image.get_size()
            self.rect.x = offsetx
            self.rect.y = offsety
            if save != None:
                self.saveFile = save
            if emulator != None:
                self.emulator = emulator
            if resize == True:
                self.image = pygame.transform.smoothscale(self.image, (int(self.size[0]/2), int(self.size[1]/2)))
            #print("Sprite made for " + save + " at: " + str(self.rect.x) + ", " + str(self.rect.y)) #debug info
            
        def destroy(self):
            pygame.sprite.Sprite.kill(self)
    
    class BG(pygame.sprite.Sprite):
        def __init__(self, imageLocation):
            super(BG, self).__init__()
            global gameFont
            global screenWidth
            global screenHeight
            self.font = gameFont
            if os.path.exists(imageLocation):
                self.image = pygame.image.load(imageLocation)
                self.image.set_colorkey((255, 255, 255), RLEACCEL)
            else:
                logging.warning(imageLocation + " does not exist!")
                self.image = pygame.Surface((screenWidth, screenHeight))
                self.image.fill((255, 0, 255))
            self.rect = self.image.get_rect()
            self.size = self.image.get_size()
        
        def destroy(self):
            pygame.sprite.Sprite.kill(self)
    
    class cursor(pygame.sprite.Sprite):
        def __init__(self, iconImage, offsetX, offsetY):
            super(cursor, self).__init__()
            global gameFont
            global screen
            self.font = gameFont
            if os.path.exists(iconImage):
                self.image = pygame.image.load(iconImage)
                self.image.set_colorkey((255, 255, 255), RLEACCEL)
            else:
                logging.warning(iconImage + " does not exist!")
                self.image = pygame.Surface((256, 256))
                self.image.fill((255, 0, 255, 125))
            self.rect = self.image.get_rect()
            self.size = self.image.get_size()
            self.image = pygame.transform.smoothscale(self.image, (int(self.size[0]/2), int(self.size[1]/2)))
            self.rect.x = offsetX
            self.rect.y = offsetY
            #print("Sprite made for cursor!") #debug info
        
        def destroy(self): #function for removing the sprite from the game
            pygame.sprite.Sprite.kill(self)
        
        # Move the sprite based on user keypresses
        def update(self, pressed_keys, totalHeight):
            #load necessary global variables
            global columnPosition
            global rowPosition
            global gameSaveSprites
            global screenWidth
            global screenHeight
            global gridX
            global gridY
            if pressed_keys == K_UP: #when the up key is depressed
                self.rect.move_ip(0, -128) #move up one grid space (128 pixels)
                rowPosition -= 1 #update the cursor's position in the grid
                if self.rect.y <= 128: #is the cursor beyond the screen?
                    self.rect.top = 128 #Set it to top of screen
                    if (gameSaveSprites[0].rect.y != 128): #is the very first game save in the very first spot on the grid?
                        for sprite in gameSaveSprites: #no? then move all game save sprites down
                            sprite.rect.y += 128
                    else: #if the game save is in the very first spot on the grid:
                        rowPosition = 0 #update the cursor's position in the grid to the minimum row position
            if pressed_keys == K_DOWN: #when the down key is depressed
                self.rect.move_ip(0, 128) #move down one grid space (128 pixels)
                rowPosition += 1 #update its position in the grid
                if self.rect.y > 768: #is the cursor beyond the screen?
                    self.rect.y = 768 #Set it to the bottom of screen
                    if (gameSaveSprites[-1].rect.y > 768): #is the final sprite at the bottom of the screen?
                        for sprite in gameSaveSprites: #no? then move all game save sprites up
                            sprite.rect.y -= 128
                    elif (gameSaveSprites[-1].rect.y == 768): #is the final row on screen?
                        rowPosition = totalHeight #if so, then rows will not move up and the cursor's position is updated to the max row height in the grid
                if self.rect.y > (128*totalHeight + 128): #is the cursor at the edge of the grid?
                    self.rect.y = (128*totalHeight + 128) #if so, keep it at the edge
                    rowPosition = totalHeight #update its position on the grid to the max row height
                if ((columnPosition + totalHeight*columnLength + 1) > len(gameSaveSprites)) and (rowPosition == totalHeight): #is the cursor about to go down a row that isn't fully filled?
                    self.rect.x = gridX + (len(gameSaveSprites) - (totalHeight*columnLength) - 1)*128 #if so, move the cursor to the last icon on the incomplete row
                    columnPosition = len(gameSaveSprites) - (totalHeight*columnLength) - 1 #update it's position in the grid
            if pressed_keys == K_LEFT: #when the left key is depressed
                self.rect.move_ip(-128, 0) #move the cursor left
                columnPosition -= 1 #update its position in the grid
                if self.rect.x <= int((screenWidth-columnLength*128)/2): #is the cursor at the edge of the grid?
                    self.rect.x = int((screenWidth-columnLength*128)/2) #if so, keep it at the edge
                    columnPosition = 0 #update its position in the grid
            if pressed_keys == K_RIGHT: #when the right key is depressed
                self.rect.move_ip(128, 0) #move the cursor right
                columnPosition += 1 #update its position in the grid
                if self.rect.x >= int((screenWidth-columnLength*128)/2 + 640): #is the cursor at the edge of the grid?
                    self.rect.x = int((screenWidth-columnLength*128)/2 + 640) #if so, keep it at the edge
                    columnPosition = columnLength - 1 #update its position in the grid to the max column length (-1 because the length doesn't start with 0 but our calculations are based on starting with 0)
                if (columnPosition + rowPosition*columnLength + 1) > len(gameSaveSprites): # is it trying to move right on an incomplete row?
                    self.rect.move_ip(-128,0) #if so, keep it at the edge
                    columnPosition = len(gameSaveSprites) - (totalHeight*columnLength) - 1 #update its position in the grid to the very last icon
                    
    class saveInfoBG(pygame.sprite.Sprite):
        def __init__(self, inputX, inputY, columnLength, screen):
            super(saveInfoBG, self).__init__()
            global saveInfoBGColor
            global saveInfoBGImage
            self.width = int(128*columnLength)
            self.height = int(((4/6)*columnLength)*128)
            if (saveInfoBGImage == None):
                logging.info("No image provided for the Save Info dialogue box")
                self.image = pygame.Surface((self.width, self.height))
                self.image.fill(saveInfoBGColor)
            else:
                self.image = pygame.image.load(saveInfoBGImage)
            self.rect = self.image.get_rect()
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            self.rect.x = inputX
            self.rect.y = inputY
            #print("Sprite made for BG!") #debug info
        
        def destroy(self):
            pygame.sprite.Sprite.kill(self)
    
    class saveInfoText(pygame.sprite.Sprite):
        def __init__(self, text, font, size, color, x, y):
            super(saveInfoText, self).__init__()
            self.font = font
            self.image = self.font.render(text, True, color)
            textWidth = self.image.get_width()
            textHeight = self.image.get_height()
            self.rect = self.image.get_rect()
            self.rect.center = (x,y)
            #self.rect.x = x
            #self.rect.y = y
        
        def destroy(self):
            pygame.sprite.Sprite.kill(self)
            
    ###  Create Sprite Groups   ###
    allSprites = pygame.sprite.Group() #creates the all sprites group
    logging.debug("...allSprites sprite group created")
    
    ###   Set Game Font   ###
    try:
        gameFont = pygame.font.SysFont("Arial.ttf", 32)
        logging.debug("...game Font loaded")
    except Exception as e:
        logging.critical("Exception occured", exc_info=True)
        sys.exit("Quitting program unexpectdly. Check error_log.txt")
    
    ###   Create Sprites   ###
    #These sprites are used constnatly throughout the game#
    BG = BG(BGImage) #create a BG object
    allSprites.add(BG) #add it to all sprites
    logging.debug("...background loaded")
    
    cursor = cursor(cursorImage, gridX, gridY) #creates the cursor object
    allSprites.add(cursor) #adds the cursor sprite to the allSprites group so it can be rendered by pygame
    logging.debug("...cursor loaded")
    
    allEmulatorSprites = loadEmulatorSprites(iconLocations, gameSaveFiles, gameSaveSprites, gridX, gridY) #the function it calls adds the individual sprites to the allSprites group, so there is no need to have a allSprites.add(allEmulatorSprites)
    logging.debug("...emulator sprites loaded")
    
    #Update global variables necessary for game logic
    totalHeight = allEmulatorSprites
    currentSave = saveFileInfo()
    logging.debug("...global variables necessary for game logic have been set")
    
    ###   Run the game   ###
    logging.debug("Launching game")
    
    while running: #while the game is running
        #Global Variable Updates
        currentPosition = columnPosition + rowPosition*columnLength #current position of cursor sprite in the grid
        
        #User Input and event management
        for event in pygame.event.get():
            if event.type == KEYDOWN: #did the user hit a key?
                if event.key == K_ESCAPE: #Escape key?
                    running = False #quit
            elif event.type == pygame.QUIT:
                running = False #setting running to False breaks the loop
            elif event.type == KEYUP: #when the key is depressed
                if event.key == K_RETURN: #if the enter key was hit
                    #print("Game Save: ", gameSaveSprites[currentPosition].saveFile) #debug info
                    #print("Cursor Position: ", columnPosition, ", ", rowPosition) #debug info
                    selectedItem = gameSaveSprites[currentPosition].saveFile
                    if currentLevel == "Main Menu":
                        resetPosition(cursor)
                        currentLevel = "Console Saves"
                        continue
                    if currentLevel == "Console Saves":
                        if selectedItem == "return":
                            resetPosition(cursor)
                            currentLevel = "Main Menu"
                        else:
                            currentLevel = "Save Info"
                        continue
                    if currentLevel == "Save Info":
                        currentLevel = "Console Saves"
                        for sprite in saveInfoList:
                            sprite.destroy()
                        saveInfoList.clear()
                        saveInfoList = []
                        continue
                if event.key == K_BACKSPACE:
                    if currentLevel == "Console Saves":
                        resetPosition(cursor)
                        currentLevel = "Main Menu"
                        continue
                    if currentLevel == "Save Info":
                        currentLevel = "Console Saves"
                        for sprite in saveInfoList:
                            sprite.destroy()
                        saveInfoList.clear()
                        saveInfoList = []
                        continue
                if currentLevel != "Save Info":
                    cursor.update(event.key, totalHeight)
        
        #Levels
        if currentLevel == "Main Menu":
            if allEmulatorSprites == None:
                for sprite in gameSaveSprites:
                    sprite.destroy()
                gameSaveSprites.clear()
                allEmulatorSprites = loadEmulatorSprites(iconLocations, gameSaveFiles, gameSaveSprites, gridX, gridY)
                totalHeight = allEmulatorSprites
                allSaveSprites = None
        if currentLevel == "Console Saves":
            if allSaveSprites == None:
                for sprite in gameSaveSprites:
                    sprite.destroy()
                gameSaveSprites.clear()
                allSaveSprites = loadGameSaveSprites(iconLocations, gameSaveFiles, gameSaveSprites, gridX, gridY, selectedItem)
                totalHeight = allSaveSprites
                allEmulatorSprites = None
            currentSave = saveFileInfo()
                
        if currentLevel == "Save Info":
            if saveInfoList == []:
                currentSave.loadSave(gameSaveSprites[currentPosition].emulator, gameSaveSprites[currentPosition].saveFile)
                saveInfoList.append( saveInfoBG(gridX, gridY, columnLength, screen) )
                saveInfoList.append( saveInfoText(currentSave.name, gameFont, 32, (255, 255, 255, 255), gridX + int(saveInfoList[0].width/2), gridY + 48) )
                loadGameSaveSprite(iconLocations, saveInfoList, gridX + int(saveInfoList[0].width/2 - 256/2), gridY + 80, gameSaveSprites[currentPosition].emulator, currentSave.icon)
                saveInfoList.append( saveInfoText("Last Played: " + currentSave.lastPlayed, gameFont, 32, (255, 255, 255, 255), gridX + int(saveInfoList[0].width/2), gridY + 352) )
                saveInfoList.append( saveInfoText("Last Saved: " + currentSave.lastSaved, gameFont, 32, (255, 255, 255, 255), gridX + int(saveInfoList[0].width/2), gridY + 400) )
                for sprite in saveInfoList:
                    allSprites.add(sprite)
                logging.debug(currentSave.name + " for the " + gameSaveSprites[currentPosition].emulator + "loaded for Save Info")
        
        ###   Draw Commands   ###
        # Fill the background with white
        #screen.fill((255, 255, 255))
        
        # Draw the sprites on the screen
        for entity in allSprites:
            screen.blit(entity.image, entity.rect)

        # Flip the display which means update the entire screen
        pygame.display.flip()
    pygame.quit()
logging.debug("Program quitting...")
sys.exit("Program quitting...")