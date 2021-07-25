def getAllLootMarkers():
    markerList = []
    for marker in ENGINE.allMapMarkers:
        if "AIRDROP" in marker:
            markerList += [marker]
    ENGINE.systemchat(str(len(markerList)))
    return markerList

lootMarkerList = getAllLootMarkers()

ENGINE.systemchat(str(getAllLootMarkers()))
ENGINE.systemchat("TEEEEST!")
for marker in lootMarkerList:
    marker.setMarkerColor("ColorYellow");
    marker.setMarkerAlpha(1)
    marker.setMarkerSizeLocal (10, 10)
await ( isNil("WEATHER_MODULE_LOADED") == False );
STATIC.publicVariable("WEATHER_MODULE_LOADED")
firstInit = False
if(isNil("SOME_MODULE_LOADED") == True):
    STATIC.publicVariable("SOME_MODULE_LOADED")
    firstInit = True

fun = 1
await (fun > 1 and fun == 0);





#
