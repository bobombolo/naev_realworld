#!/usr/bin/python
import os
import shutil
import math
from random import randint
import lxml.etree
import lxml.builder
import csv
import sys 
reload(sys) 
sys.setdefaultencoding("utf-8")
import unicodedata

import ogr
import subprocess

inraster = 'spreadsheets/HYP_HR_SR_OB_DR.tif'
#inshape = 'spreadsheets/buffers.shp'
#inraster_width = 21600
#inraster_height = 10800

hex_width = 11.547
hex_height = 10

max_ppop = 35676000

def angle_trunc(a):
    while a < 0.0:
        a += math.pi * 2
    return a

def getAngleBetweenPoints(x_orig, y_orig, x_landmark, y_landmark):
    deltaY = y_landmark - y_orig
    deltaX = x_landmark - x_orig
    return angle_trunc(math.atan2(deltaY, deltaX))

#ds = ogr.Open(inshape)
#lyr = ds.GetLayer(0)

#def create_planet_graphic(cityid):
def create_planet_graphic(longit, latit, ppop, name, sunx, suny):
        
    radius = 1 #this is in degrees and if too large captures too much of the basemap and all nearby planets look the same
    
    sun_angle = getAngleBetweenPoints(longit, latit, sunx, suny)
    sun_angle = math.degrees(sun_angle)
    #print sun_angle
    
    sun_elev = 90-(((math.sqrt((sunx-longit)**2+(suny-latit)**2))/11.547)*90)
    #print sun_elev
    
    xmin = str(longit - radius)
    ymin = str(latit - radius)
    xmax = str(longit + radius)
    ymax = str(latit + radius)
    #lyr.ResetReading()    
    outraster = "tmp/"+name+".bmp"
    if not os.path.isfile(outraster):
        size = subprocess.check_output(['gdalwarp', '-te', xmin,ymin,xmax,ymax,'-of','BMP', '-overwrite', inraster,outraster])
        size = size[29:size.find('L.')].split('P x ')[0] #with radius 1 this gives 120pixels wide
        os.unlink('tmp/'+name+'.bmp.aux.xml')
    else:
        size = "120"
    
    if  ppop  > 10000000:
        modifier = 240 + (120*ppop/max_ppop)
    elif ppop > 1000000:
        modifier = 120 + (120*ppop/10000000)
    elif ppop > 100000:
        modifier = 120*ppop/1000000
    else:
        modifier = 0
    #print ppop
    #print modifier #add size to planets based on population max is 450
    pixel_width = int(size) + modifier
    image_radius = str(pixel_width/2-0.5)
    pixel_width = str(pixel_width)
    
    print pname+": "+pixel_width
    #-fill rgb(255,255,255) -colorize 0,0,50 to colorize according to temperature?
    
    subprocess.call(['convert', '-size', pixel_width+'x'+pixel_width, 'xc:black', '-fill', 'white',
                     '-draw', 'circle '+image_radius+','+image_radius+' '+image_radius+',0','tmp/sphere_mask.png'])
    
    subprocess.call(['convert', '-size', pixel_width+'x'+pixel_width, 'xc:', '-channel', 'R',
          '-fx', 'yy=(j+.5)/h-.5; (i/w-.5)/(sqrt(1-4*yy^2))+.5',
          '-separate',  '+channel','tmp/sphere_lut.png'])
    
    subprocess.call(['convert', 'tmp/sphere_mask.png',
          '(', '+clone', '-blur', '0x20', '-shade', str(sun_angle)+'x'+str(sun_elev), '-contrast-stretch', '0%',
             '+sigmoidal-contrast', '6x50%', '-fill', 'grey50', '-colorize', '10%',  ')',
          '-composite', 'tmp/sphere_overlay.png'])
    
    subprocess.call(['convert', outraster, '-resize', pixel_width+'x'+pixel_width,
          'tmp/sphere_lut.png', '-fx', 'p{ v*w, j }',
          'tmp/sphere_overlay.png', '-compose', 'HardLight',  '-composite',
          'tmp/sphere_mask.png', '-alpha', 'off', '-compose', 'CopyOpacity', '-composite',
          'gfx/planet/space/mapped/'+name+'.png'])
    
    #os.unlink(outraster)
    
    return 1

def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

SOURCEFOLDER = 'spreadsheets/'
SYSFILE = SOURCEFOLDER+"star_systems_hex_based_sorted.csv"
PLANETFILE=SOURCEFOLDER+"planets_stations_hexid_adm1_climate_sorted.csv"
FACTIONFILE=SOURCEFOLDER+"factions.csv"
GENFOLDER = ""

if os.path.exists("ssys"):
    shutil.rmtree("ssys")
os.makedirs("ssys")
if os.path.exists("assets"):
    shutil.rmtree("assets")
os.makedirs("assets")

"""faction conversion"""
faction_dict = {
    "NULL":"Pirate",
    "Asia": "Goddard",
    "North America": "Empire",
    "Europe": "Proteron",
    "Africa":"Dvaered",
    "South America":"Za'lek",
    "Oceania":"Sirius",
    "Australia":"Soromid",
    "Antarctica":"FLF"
}
"""translate the MAPCOLOR9 field to naev colors"""
color_dict = {
    "1.00":"green",
    "2.00":"red",
    "3.00":"orange",
    "4.00":"yellow",
    "5.00":"blue",
    "6.00":"cyan",
    "7.00":"purple",
    "8.00":"brown",
    "9.00":"aqua",
    "10.00":"silver",
    "11:00":"darkBlue",
    "12:00":"gold",
    "13:00":"darkRed"
}
"""graphic lists"""
planet_exteriors  = "aquatic2.png,aquatic3.png,aquatic.png,asteroid.png,desertic2.png,desertic3.png,desertic4.png,desertic.png,forest2.png,forest.png,gas.png,lava.png,methane.png,mining2.png,mining3.png,mining4.png,mining5.png,mining6.png,mining.png,oceanic2.png,oceanic.png,rocky_small.png,snow.png,snowy_cliffs.png".split(',')
battle_stations   = "001.png,station-battlestation.png,station-fleetbase.png,station-fleetbase2.png,station-fleetbase3.png".split(',')
shipyards         =  "station-shipyard.png,station-shipyard2.png".split(',')
station_exteriors =  "station03.png,station04.png,station05.png,traderoom.png".split(',')

"""build faction list"""
"""
FNAMEFIELD = "SOVEREIGNT"
faction_counter = 0
with open(FACTIONFILE, 'rb') as factionlist:
    G = lxml.builder.ElementMaker()
    FACTIONS = G.Factions
    FFACTION = G.faction
    FSTATIC = G.static
    FINVISIBLE = G.invisible
    FDISPLAY = G.display
    FLOGO = G.logo
    FPLAYER = G.player
    FCOLOR = G.color
    FSPAWN = G.spawn
    FEQUIP = G.equip
    FSTANDING = G.standing
    FALLIES = G.allies
    FA_ALLY = G.ally
    FENEMIES = G.enemies
    FE_ENEMY = G.enemy
    
    factionxml = FACTIONS()
    
    factions = csv.DictReader(factionlist)
    for rowf in factions:
        if rowf['TYPE'] == "Sovereign country" or rowf['TYPE'] == "Country":
            fname = remove_accents(rowf[FNAMEFIELD])
            
            factionxml.append(FFACTION(
                FSTATIC(),
                FINVISIBLE(),
                FDISPLAY(fname),
                FLOGO("flags/"+fname),
                FPLAYER("0"),
                
                name=fname
            ))
            faction_counter = faction_counter+1
        
    dump3 = lxml.etree.tostring(factionxml, xml_declaration=True, encoding='utf-8', pretty_print=True)
    print dump3
    filename = GENFOLDER + "faction.xml"
    FILE = open(filename,"w")
    FILE.writelines(dump3)
    FILE.close()
    print "factions: "+str(faction_counter)
"""
        
NAMEFIELD = "NAMEASCII"
NEIGHBORSFIELD = "NEIGHBORS"
POPFIELD = "POPULATION"
XFIELD = "sys_xcoord"
YFIELD = "sys_ycoord"
SYSXFIELD = "cent_xcoor"
SYSYFIELD = "cent_ycoor"

PNAMEFIELD = "NAMEASCII"
PFACTIONFIELD = "ADM0NAME"
PPOPFIELD = "POP_MAX"
PPOP_CUTOFF = 100000
PXFIELD = "X"
PYFIELD = "Y"
SYS_KEY = "HEX_ID"
SYS_FK = "HEX_ID"


sysradmin = 16000.0
sysradmax = 64000.0
x_scale = 10
y_scale = 12
sys_r_scale = 20000
px_scale = 8000
py_scale = 8000
plan_lim = 8

system_counter = 0
jump_counter = 0
planet_counter = 0

with open(SYSFILE, 'rb') as systemlist:
    systems = csv.DictReader(systemlist)
    for row in systems:
        E = lxml.builder.ElementMaker()
        SSYS = E.ssys
        GENERAL = E.general
        G_RADIUS = E.radius
        G_STARS = E.stars
        G_INTERFERENCE = E.interference
        G_NEBULA=E.nebula
        """background refers to the script in dat/bkg that"""
        G_BACKGROUND=E.background
        POS = E.pos
        P_X = E.x
        P_Y = E.y
        
        ASSETS = E.assets
        ASSET = E.asset
        JUMPS = E.jumps
        JUMP = E.jump
        JPOS = E.pos
        JAUTOPOS = E.autopos
        name = remove_accents(row[NAMEFIELD])
        neighbors = row[NEIGHBORSFIELD]
        
        ssys = SSYS(name=name)
        sysradius = (hex_width/2)*px_scale
        """
        sysradius = sysradmax
        if sysradius < sysradmin:
            sysradius = sysradmin
        if sysradius > sysradmax:
            sysradius = sysradmax
        print sysradius"""
        ssys.append(
            GENERAL(
                G_RADIUS('{:.6f}'.format(sysradius)),
                G_STARS('{:.0f}'.format(100)),
                G_INTERFERENCE('{:.6f}'.format(0)),
                G_NEBULA('{:1.1f}'.format(0), volatility='{:1.1f}'.format(0))))
        sysx = float(row[XFIELD])
        sysy = float(row[YFIELD])
        ssys.append(
            POS(
                P_X('{:.6f}'.format(sysx*x_scale)),
                P_Y('{:.6f}'.format(sysy*y_scale)),
            ))
        
        sys_continent = row['CONTINENT']
        if sys_continent == "":
            sys_continent = "NULL"
        cent_x = float(row[SYSXFIELD])
        cent_y = float(row[SYSYFIELD])
        ssys_assets = ASSETS()
        ssys_jumps = JUMPS()
        """load cities for each country/state as the planets"""  
        with open(PLANETFILE, 'rb') as planetlist:
            planets = csv.DictReader(planetlist)
            sysplanet_counter = 0
            shipyard = 0
            militarybase = 0
            
            for rowp in planets:
                if rowp[SYS_KEY] == row[SYS_FK]:
                    skip = 0
                    ppop = int(rowp[PPOPFIELD])
                    """get absolute planet coords"""
                    planx = float(rowp[PXFIELD])
                    plany = float(rowp[PYFIELD])
                    
                    if rowp['featurecla'] == "Airport" and militarybase < 1:
                        pname = remove_accents(rowp['name'].replace("/","-").replace("Int'l",rowp['abbrev']))+" Stn"
                        graphic_space = battle_stations[randint(0,len(battle_stations)-1)]
                        graphic_ex = station_exteriors[randint(0,len(station_exteriors)-1)]
                        militarybase += 1
                        presence_faction = faction_dict[sys_continent]
                        presence_value = int(rowp['natlscale'])*10
                        presence_range = int(rowp['scalerank'])
                    elif rowp['featurecla'] == "Port" and shipyard < 1:
                        pname = remove_accents(rowp['name'].replace("/","-"))+" Ship Yards"
                        graphic_space = shipyards[randint(0,len(shipyards)-1)]
                        graphic_ex = station_exteriors[randint(0,len(station_exteriors)-1)]
                        shipyard += 1
                        presence_faction = faction_dict[sys_continent]
                        presence_value = 1
                        presence_range = 2
                    elif sysplanet_counter < plan_lim or rowp['ADM0CAP'] == "1":
                        pname = remove_accents(rowp['name']+", "+remove_accents(rowp['adm1_name']))
                        if create_planet_graphic(planx, plany, ppop, pname, cent_x,cent_y):
                            graphic_space = 'mapped/'+pname+'.png'
                        else:
                            graphic_space = 'M'+'{0:02d}'.format(randint(0,13))+'.png'
                        graphic_ex = planet_exteriors[randint(0,len(planet_exteriors)-1)]
                        sysplanet_counter += 1
                        presence_faction = faction_dict[sys_continent]
                        presence_value = 1
                        presence_range = 1
                        
                        """use climate data to derive planet class and graphics"""
                        
                        
                    else:
                        skip = 1
                    if skip == 0:
                        pdesc = pname + " is in the " + name + " system."
                        if rowp["ADM0NAME"] != "0":
                            pdesc += "It is part of "+remove_accents(rowp['ADM0NAME'])
                        if rowp['adm1_name'] != "" and rowp['CONTINENT'] != "Antarctica":
                            if rowp['adm1_type_'] =="":
                                padm1_type = "area"
                            else:
                                padm1_type = remove_accents(rowp['adm1_type_'])
                            pdesc += " in the "+padm1_type+" of "+remove_accents(rowp['adm1_name'])+"."
                        else:
                            pdesc += "."
                        
                        ssys_assets.append(ASSET(pname))
                        """generate the asset xml file"""
                        F = lxml.builder.ElementMaker()
                        ASSET2 = F.asset
                        PPOS = F.pos
                        PPX = F.x
                        PPY = F.y
                        GFX = F.GFX
                        GFX_SPACE = F.space
                        GFX_EXTERIOR = F.exterior
                        PRESENCE = F.presence
                        PRES_FACTION = F.faction
                        PRES_VALUE = F.value
                        PRES_RANGE = F.range
                        PGENERAL = F.general
                        PG_CLASS = F.howTotallyAnnoyingIsThis
                        PG_POP = F.population
                        PG_HIDE = F.hide
                        PG_SERVICES = F.services
                        PGS_LAND = F.land
                        PGS_REFUEL = F.refuel
                        PGS_BAR = F.bar
                        PGS_MISSIONS = F.missions
                        PGS_COMMODITY = F.commodity
                        PGS_OUTFITS = F.outfits
                        PGS_SHIPYARD = F.shipyard
                        PG_COMMODITIES = F.commodities
                        PGC_COMMODITY = F.commodity
                        PG_DESC = F.description
                        PG_BAR = F.bar
                        TECH = F.tech
                        TECHITEM = F.item
                        
                        asset = ASSET2(name=pname)
                        
                        """subtract from  system centroid asolute coord to get relative coord"""
                        """stretch the relative position across the system for looks"""
                        plan_rel_x = (planx-cent_x)*px_scale
                        plan_rel_y = (plany-cent_y)*py_scale
                        
                        asset.append(
                            PPOS(
                                PPX('{:.6f}'.format(plan_rel_x)),
                                PPY('{:.6f}'.format(plan_rel_y)),
                            )
                        )
                        
                        
                        
                        asset.append(
                            GFX(
                                GFX_SPACE(graphic_space),
                                GFX_EXTERIOR(graphic_ex)
                            )
                        )                    
                        
                        """game crash if presence left empty"""
                        asset.append(
                            PRESENCE(
                                PRES_FACTION(presence_faction),
                                PRES_VALUE('{:.6f}'.format(presence_value)),
                                PRES_RANGE(str(presence_range)),
                            )
                        )
                        """battlestation services and tech"""
                        if rowp['featurecla'] == "Airport":
                            asset.append(
                                PGENERAL(
                                    PG_CLASS("M"),
                                    PG_POP('{:.0f}'.format(ppop)),
                                    PG_HIDE('{:.6f}'.format(0)),
                                    PG_SERVICES(
                                        PGS_LAND(),
                                        PGS_REFUEL(),
                                        PGS_BAR(),
                                        PGS_OUTFITS(),
                                    ),
                                    PG_COMMODITIES(),
                                    PG_DESC(pdesc),
                                    PG_BAR("This is the officer's lounge"),
                                )
                            )
                            
                            asset.append(
                                TECH(
                                    TECHITEM("All Outfits")
                                )
                            )
                        
                        elif rowp['featurecla'] == "Port":
                            """shipyard services and tech"""
                            asset.append(
                                PGENERAL(
                                    PG_CLASS("M"),
                                    PG_POP('{:.0f}'.format(ppop)),
                                    PG_HIDE('{:.6f}'.format(0)),
                                    PG_SERVICES(
                                        PGS_LAND(),
                                        PGS_REFUEL(),
                                        PGS_BAR(),
                                        PGS_OUTFITS(),
                                        PGS_SHIPYARD(),
                                    ),
                                    PG_COMMODITIES(),
                                    PG_DESC(pdesc),
                                    PG_BAR("Shipyard workers drink here"),
                                )
                            )
                            
                            asset.append(
                                TECH(
                                    TECHITEM("All Ships"),
                                    TECHITEM("All Outfits")
                                )
                            )
                        else:
                            """populated planets services and tech"""
                            asset.append(
                                PGENERAL(
                                    PG_CLASS("M"),
                                    PG_POP('{:.0f}'.format(ppop)),
                                    PG_HIDE('{:.6f}'.format(0)),
                                    PG_SERVICES(
                                        PGS_LAND(),
                                        PGS_REFUEL(),
                                        PGS_BAR(),
                                        PGS_MISSIONS(),
                                        PGS_COMMODITY(),
                                        PGS_OUTFITS()
                                    ),
                                    PG_COMMODITIES(
                                        PGC_COMMODITY("Food"),
                                        PGC_COMMODITY("Ore"),
                                        PGC_COMMODITY("Industrial Goods"),
                                        PGC_COMMODITY("Medicine"),
                                        PGC_COMMODITY("Luxury Goods"),
                                        ),
                                    PG_DESC(pdesc),
                                    PG_BAR("Humans often drink at bars..."),
                                )
                            )
                            if rowp['WORLDCITY']=="1":
                                asset.append(
                                    TECH(
                                        TECHITEM("Basic Outfits 2"),
                                    )
                                )
                            elif rowp['MEGACITY']=="1":
                                asset.append(
                                    TECH(
                                        TECHITEM("Basic Outfits 2"),
                                    )
                                )
                            elif rowp['ADM0CAP']=="1":
                                asset.append(
                                    TECH(
                                        TECHITEM("Basic Outfits 2"),
                                    )
                                )
                            else:
                                asset.append(
                                    TECH(
                                        TECHITEM("Basic Outfits 1"),
                                    )
                                )
    
                        dump2 = lxml.etree.tostring(asset, xml_declaration=True, encoding='utf-8', pretty_print=True)
                        dump2 = dump2.replace("howTotallyAnnoyingIsThis", "class")
                        """print dump2"""
                        filename = GENFOLDER + "assets/" + pname.lower() + ".xml"
                        FILE = open(filename,"w")
                        FILE.writelines(dump2)
                        FILE.close()
                        
        if (sysplanet_counter+militarybase+shipyard) > 0:
            ssys.append(ssys_assets)
        
        if neighbors != "":
            """print neighbors"""
            sysjump_counter = 0
            for jumpname in neighbors.split(','):
                """print jumpname"""
                jname = remove_accents(jumpname)
                
                ssys_jumps.append(JUMP(
                                       JAUTOPOS(),
                                       target=jname
                                       )
                                 )
                sysjump_counter = sysjump_counter+1
        if sysjump_counter > 0:
            ssys.append(ssys_jumps)
        
        dump = lxml.etree.tostring(ssys, xml_declaration=True, encoding='utf-8', pretty_print=True)
        """print dump"""
        filename = GENFOLDER + "ssys/" + name.lower() + ".xml"
        FILE = open(filename,"w")
        FILE.writelines(dump)
        FILE.close()
        jump_counter = jump_counter+sysjump_counter
        planet_counter = planet_counter+sysplanet_counter
        system_counter = system_counter+1
        print "built the "+name+" system with "+str(sysplanet_counter+militarybase+shipyard)+" assets and "+str(sysjump_counter)+" jumps"
        """print "planets: " + str(planet_counter)"""
       
    print "TOTALS: systems: " + str(system_counter) + ", jumps: " + str(jump_counter) + ", assets: " + str(planet_counter)