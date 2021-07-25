getAllLootMarkers = {
   private _markerList = [];
   {
      private _marker = _x;
      if ("AIRDROP" in _marker) then {
         _markerList = _markerList + [_marker];
      };
   } forEach allMapMarkers;
   systemchat(str(count(_markerList)));
   if (true) exitWith {_markerList};
   
};
private _lootMarkerList =  call getAllLootMarkers;
systemchat(str( call getAllLootMarkers));
systemchat("TEEEEST!");
{
   private _marker = _x;
   _marker setMarkerColor("ColorYellow");
   _marker setMarkerAlpha(1);
   _marker setMarkerSizeLocal[10,10];
} forEach _lootMarkerList;
waitUntil {isNil("WEATHER_MODULE_LOADED") == false};
publicVariable("WEATHER_MODULE_LOADED");
private _firstInit = false;
if (isNil("SOME_MODULE_LOADED") == true) then {
   publicVariable("SOME_MODULE_LOADED");
   _firstInit = true;
};
private _fun = 1;
waitUntil {(_fun > 1)&&(_fun == 0)};
