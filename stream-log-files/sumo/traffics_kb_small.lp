% Instance data


% Road structure of nodes and (taken from background KB)
node(i1).
node(i2).
node(i3).
node(i4).
node(i5).
node(gneJ1).
node(gneJ13).
node(lnk1).
node(o1).
node(o4).
node(o5).

link(i1,i1b,we).
link(i1b,gneJ1,we).
link(i2,i2b,we).
link(i2b,gneJ1,we).
link(gneJ1,lnk1a,we).
link(lnk1a,lnk1b,we).
link(gneJ1,o1b,ew).
link(o1b,o1,ew).
link(lnk1b,lnk1a,ew).
link(lnk1a,gneJ1,ew).

link(lnk1b,lnk1c,we).
link(lnk1c,gneJ13,we).
link(gneJ13,o5b,we).
link(o5b,o5,we).
link(gneJ13,o4b,we).
link(o4b,o4,we).
link(gneJ13,lnk1c,ew).
link(lnk1c,lnk1b,ew).
link(i4,i4b,ew).
link(i4b,gneJ13,ew).
link(i3,i3b,ew).
link(i3b,gneJ13,ew).
link(i5,i5b,ew).
link(i5b,gneJ13,ew).
link(gneJ13,o5b,ew).
link(o5b,o5,ew).

maxSpeed(lnk1b,lnk1c,60).

maxSpeed(X,Y,50) :- link(X,Y,D), not maxSpeed(X,Y,S).


% Traffic distribution on intersection
link_ratio(gneJ1, lnk1a, we, 100). % Ratio 100/100
link_ratio(gneJ1, o1b, ew, 100). % Ratio 100/100

link_ratio(gneJ13, o4b, we, 50). % Ratio 50/100
link_ratio(gneJ13, o5b, we, 50). % Ratio 50/100
link_ratio(gneJ13, lnk1c, ew, 75). % Ratio 75/100
link_ratio(gneJ13, o5b, ew, 25). % Ratio 25/100

% Traffic light red phases, first argument is incoming node,
% second is intersection node

% This signals are not allowed to be read at the same time
conflict_tl(gneJ1, i2b, i1b).
conflict_tl(gneJ1, i2b, lnk1a).
conflict_tl(gneJ13, i3b, i4b).
conflict_tl(gneJ13, i3b, lnk1c).
conflict_tl(gneJ13, i5b, i4b).
conflict_tl(gneJ13, i5b, lnk1c).
% Inverse
conflict_tl(X, Y, Z) :- conflict_tl(X, Z, Y).

% Vehicles types
vehType(green) . # VW
vehType(red) . # Fiat
vehType(blue) . # BMW
vehType(yellow) . # Bus
vehType(black) . # Toyota

% Vehicle classification
isSubType(green, familyCar) .
isSubType(red, miniCar) .
isSubType(blue, sportsCar) .
isSubType(black, familyCar) .
isSubType(yellow, bus) .
isSubType(familyCar, vehicle) .
isSubType(miniCar, vehicle) .
isSubType(sportsCar, vehicle) .
isSubType(bus, utilVehicle) .
