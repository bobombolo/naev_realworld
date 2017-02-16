# naev_realworld
tools to generate a dat folder full of systems and planets that reflect major world cities

basically you need the source spreadsheets, and the python script to build xml files and the graphics for all the planets
the source map is downloadable at http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/raster/HYP_HR_SR_OB_DR.zip

depends: to build the images you need gdal and imagemagick

the fork where I have generated all this is into the master build of naev is at https://github.com/bobombolo/naev/tree/realworld/dat from there you could just download the dat/ssys/, dat/assets/ and dat/gfx/planets/space/mapped/ as well as the modified dat/tech.xml and dat/start.xml and drop them in your copy of naev and it should work.

DONE:
-the world was covered by a hex grid, each hex is 10 degrees of lattitude high, the largest city in that hex becomes the name for the hex. The system is then placed on the universe according to the city's real world coordinates. Within the system however, the hex centroid is used for the system centroid, neighbors calculated according to the hex are placed at the system boundaries and about 8-9 additional planets (most populous) are placed relative to eachother according to real world coordinates if they exist. One Station and one Shipyard is also placed. Factions settings and available outfits / ships / services set according to planetary or station specs, though not too sophisticated yet.

-graphics generated from real world basemap, the planet are a crop of their real world topography, with shading to indicate distance and direction to the system center (sun), and size relative to the city population.

-tech that breaks the game (basically maps for systems that don't exist) and start point edited to avoid crashes

-factions translated to continent, so spawning, etc works.

TODO:
-only cargo missions from the mission screen on planets work. the idea is to build a find/replace planet and system names from the existing missions to work with the new universe... possibly replacing the names of the factions with the names of real world military alliances... possibly revamping the existing missions to be more generic.

-more work needs to be done on deciding which systems get which outfits which might require some group heirarchy in the tech.xml file

-adding of some planets, asteroids and stations to represent more real world features such as volcanoes (lava planets), lakes (ocean planets), etc.

-currently airports are used as military bases, ports as shipping yards, could have more variety and better data sources for these

-the source spreadsheets include average annual temperature and precipitation, as well as elevation for the cities, which could be used to further customize the planet graphics both from space and once landed, as well as availability of various commodities, etc... source files for real world commodities and mineral and other raw resources and crops would be useful for deciding commodities. the source spreadsheets include economic status, gdp, income_grp, population and other attributes that could be useful in further differentiating systems, faction presence, etc.


here are some screenshots:

![screenshot from 2017-02-16 16-17-41](https://cloud.githubusercontent.com/assets/25610408/23041742/f46f42f0-f463-11e6-8f83-f84848e81a52.png)
![screenshot from 2017-02-16 16-17-59](https://cloud.githubusercontent.com/assets/25610408/23041743/f46fd10c-f463-11e6-9e63-b6dc03e177c1.png)
![screenshot from 2017-02-16 16-19-22](https://cloud.githubusercontent.com/assets/25610408/23041744/f46fda3a-f463-11e6-86a8-f25945255d77.png)
![screenshot from 2017-02-16 16-20-21](https://cloud.githubusercontent.com/assets/25610408/23041741/f46c02d4-f463-11e6-8ede-6d4c5efac9f5.png)
![screenshot from 2017-02-16 16-25-05](https://cloud.githubusercontent.com/assets/25610408/23041853/82002bac-f464-11e6-9e63-3c2b03157eb4.png)
