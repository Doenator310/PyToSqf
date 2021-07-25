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
    if isNil(x):
        a += 22
        pass
    else:
        a = 0





#
