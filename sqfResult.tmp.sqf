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
   if (isNil(_x)) then {
      private _a = _a + 22;

   } else {
      _a = 0;
   };
} forEach _lootMarkerList;
