def GetAllLootMarkers():
    markerList = []
    for marker in ENGINE.allMapMarkers:
        if "AIRDROP" in marker:
            markerList += [marker]
    ENGINE.systemchat(str(len(markerList)))
    return markerList

lootMarkerList = GetAllLootMarkers()

ENGINE.systemchat(str(GetAllLootMarkers()))
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
if  not ("x" in "") or not 1 == 2 :
    pass
posi = (1,2,3)
fun = 1
await (fun > 1 and fun == 0);
ENGINE.spawn(GetAllLootMarkers, "A", "B","C")
ENGINE.spawn(GetAllLootMarkers)




#
