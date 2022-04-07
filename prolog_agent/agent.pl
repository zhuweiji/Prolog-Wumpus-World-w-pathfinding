% delete all references to these values, which are variable we will use
:- abolish(hunter/3).
:- abolish(visited/2).
:- abolish(stench/2).
:- abolish(tingle/2).
:- abolish(wall/2).
:- abolish(possibleWumpus/2).

% tells the compiler that these are variables which will change at runtime
:- dynamic([
    hunter/3,
    visited/2,
    stench/2,
    tingle/2,
    wall/2,

    possibleWumpus/2,
    possibleConfundus/2,
    wumpusAlive/1,
    hasarrow/1,
    numGoldCoins/1
]).

% ================== FACTS - This section contains the knowledge that the agent starts with ===========================

% facts that will always be true - even if the agent teleports to another location
hunterAlive(true).

% instantiate the relative coords and facing of the agent.
% at any time there should only be one value of hunter(x,y,d) -- use edithunter to modify hunter coords
hunter(1,1, rnorth).
visited(1,1).

% facts that may change over time.
wumpusAlive(true).
hasarrow(true).
hasgold(false).
iscounfounded(false).

% ======================================= END FACTS ========================================================================

% ===================== PERCEPTS - Implements the knowledge the agent will gain as it traverses the map =======

% add fact that stench is at square, and note possible wumpus locations
addStenchKnowledge([X,Y]) :- 
    assertz(stench(X,Y))
    , getAdjacentRooms([X,Y], AdjRooms)
    , addPossibleWumpus(AdjRooms).

% iterate over list of rooms - if room has not been visited then add a marker that Wumpus may be there
addPossibleWumpus([Room|AdjRoomsTail]) :-
    [X,Y] = Room
    , (( \+ visited(X,Y), assertz(possibleWumpus(X,Y)) ) ; true)
    , (\+AdjRoomsTail=[], addPossibleWumpus(AdjRoomsTail)) ; true
    .

verifyPossibleWumpus(OwnRoom, AdjRoom) :-
    [OX,OY] = OwnRoom
    , [WX, WY] = AdjRoom
    ,!
    , (
        possibleWumpus(WX, WY) ->
        (\+ stench(OX,OY) -> retractall(possibleWumpus(WX, WY)), format('Wumpus not in room (~w,~w)~n', [WX, WY]))
        ; true
    )
    .

% add fact that tingle is at square, and note possible portal locations
addTingleKnowledge([X,Y]) :- 
    assertz(tingle(X,Y))
    , getAdjacentRooms([X,Y], AdjRooms)
    , addPossibleConfundus(AdjRooms).

% iterate over list of rooms - if room has not been visited then add a marker that portal may be there
addPossibleConfundus([Room|AdjRoomsTail]) :-
    [X,Y] = Room
    , (( \+ visited(X,Y), assertz(possibleConfundus(X,Y)) ) ; true)
    , (\+AdjRoomsTail=[], addPossibleConfundus(AdjRoomsTail)) ; true
    .

verifyPossibleConfundus(OwnRoom, AdjRoom) :-
    [OX,OY] = OwnRoom
    , [CX, CY] = AdjRoom
    ,!
    , (
        possibleConfundus(CX,CY) -> 
        (\+ tingle(OX,OY) -> retractall(possibleConfundus(CX, CY)), format('Confundus not in room (~w,~w)~n', [CX, CY]))
        ; true
    )
    .

% add fact that wall is in front. 
addWallKnowledge:- 
    hunter(X,Y,D)
    , getForwardRoom([X,Y,D], [X1,Y1])
    , assertz(wall(X1,Y1))
    . 

updateWumpusKilled :- 
    retractall(wumpusAlive(_))
    , retractall(possibleWumpus(_,_))
    , retractall(stench(_,_))
    , assertz(wumpusAlive(false))
    .

addGoldCoin :-
    numGoldCoins(X),
    X1 is X+1,
    retractall(numGoldCoins(_)),
    assertz(numGoldCoins(X1)).

% Update agent knowledge of the world with the percepts it is given
usePrecepts([X,Y], Confounded, Stench, Tingle, Glitter, Bump, Scream) :-
    (Confounded=on -> reborn                 ; true 
    , Stench=on -> addStenchKnowledge([X,Y]) ; true
    , Tingle=on -> addTingleKnowledge([X,Y]) ; true
    , Glitter=on -> pickup                   ; true
    , Bump=on -> addWallKnowledge            ; true
    , Scream=on -> updateWumpusKilled        ; true
    ); true
    .

% when moving in a new cell, the knowledge that some percepts are not detected is information in itself
inferIfLackOfPrecepts([X,Y]) :-
    getAdjacentRooms([X,Y], AdjRooms)
    , verifyInformationInAdjRooms([X,Y], AdjRooms)
    .
    
verifyInformationInAdjRooms([X,Y], AdjRooms) :-
    [AdjRoom|AdjRoomsTail] = AdjRooms
    , verifyPossibleWumpus([X,Y], AdjRoom)
    , verifyPossibleConfundus([X,Y], AdjRoom)
    
    , (AdjRoomsTail = [], verifyInformationInAdjRooms([X,Y], AdjRoomsTail)) ; true.
    

stopexplore(X,Y) :-
    X >= 7
    ; X =< 0
    ; Y >= 7
    ; Y =< 0
    .

roomIsDangerous(X,Y) :-
    possibleWumpus(X, Y)
    ; possibleConfundus(X, Y)
    .

fwdRoomNotSafe(X,Y, D) :-
    getForwardRoom([X,Y,D], [X1,Y1])
    , roomIsDangerous(X1, Y1)
    .

fwdRoomNotVisited(X,Y, D) :-
    getForwardRoom([X,Y,D], [X1,Y1])
    , \+ visited(X1,Y1)
    .   

fwdRoomIsWall(X,Y,D) :-
    getForwardRoom([X,Y,D], [X1,Y1])
    ,!, wall(X1,Y1)
    .

explore(L) :-
    hunter(X,Y,D) ->
    bexplore([X,Y,D], L).

% generate a list of actions to another (safe) cell using the agent's knowledge of the world
bexplore([X0,Y0,D0], [Action|ListOfActions]) :-
    (
        % format('~w~n',[ListOfActions]),
        % if explore tries to go > 7 cells exploration has definitely failed
        % (stopexplore(X0,Y0) -> false)
        
        % turn and continue exploration if room in front is not safe
        ( (fwdRoomNotSafe(X0,Y0,D0); fwdRoomIsWall(X0,Y0,D0))
            , simPerformTurn([X0,Y0,D0],[X1,Y1,D1], Action)
            , bexplore([X1,Y1,D1], ListOfActions)
            )

        % stop exploration when next room in front is not visited
        ; (\+ visited(X0,Y0))

        % otherwise recurse and find a solution that meets base cases
        ; (
            simPerformAction([X0,Y0,D0],[X1,Y1,D1], Action)
            , bexplore([X1,Y1,D1], ListOfActions)
        )
    )
    .

moveforward([X0,Y0,D0],[X1,Y1, D0]) :-
    getForwardRoom([X0,Y0,D0],[X1,Y1]).

turnleft([X,Y,D0],[X,Y, D1]) :-
    leftof(D0,D1).

turnright([X,Y,D0],[X,Y, D1]) :-
    rightof(D0,D1).

pickup :- true.
shoot :- true.

    
% simPerformActions(_,_, []).
% simPerformActions([X0,Y0,D0],[X1,Y1,D1], [Action|Tail]) :- 
%     simPerformAction(Action)
%     , simPerformActions(Tail)
%     .   

simPerformAction([X0,Y0,D0],[X1,Y1,D1], Action) :-
    (Action=moveforward -> moveforward([X0,Y0,D0],[X1,Y1, D0]))
    ; (Action=turnleft -> turnleft([X0,Y0,D0],[X1,Y1, D1]))
    ; (Action=turnright -> turnright([X0,Y0,D0],[X1,Y1, D1]))
    % ; (Action=shoot -> shoot)
    % ; (Action=pickup -> pickup)
    .

simPerformTurn([X0,Y0,D0],[X1,Y1,D1], Action) :-
    (Action=turnleft -> turnleft([X0,Y0,D0],[X1,Y1, D1]))
    ; (Action=turnright -> turnright([X0,Y0,D0],[X1,Y1, D1]))
    .

% findSafeRoom(L, ResultX, ResultY) :-
%     [H|T] = L
%     , [X,Y] = H
%     , getAdjacentRooms([X,Y], AdjRooms)
%     , filterSafeRooms(AdjRooms, SafeAdjRooms)
%     , filterUnvisitedRooms(SafeAdjRooms, UnvisitedRooms)
%     .

% filterSafeRooms(L, R) :-
%     [H|T] = L
%     , [X,Y] = H
%     , (\+possibleWumpus(X,Y), \+possibleConfundus(X,Y), \+wall(X,Y), append([X,Y], R, R)) ; true
%     , (\+ T=[], filterSafeRooms(T,R)) ; true
%     .

% filterUnvisitedRooms(L,R) :-
%     [H|T] = L
%     , [X,Y] = H
%     ,((\+ visited(X,Y), append([X,Y],R,R)); true)
%     ,((\+ T=[], filterUnvisitedRooms(T,R)) ; true)
%    .

% =========== ACTIONS - base actions that the agent can perform 

% execute a set of actions, moving the agent through the world. Agent is given list of percepts noticed in the new cell.
move(ListOfActions, Confounded, Stench, Tingle, Glitter, Bump, Scream) :-
    performActions(ListOfActions)
    , hunter(X,Y,_)
    ,!
    , usePrecepts([X,Y], Confounded, Stench, Tingle, Glitter, Bump, Scream)
    ,!
    , inferIfLackOfPrecepts([X,Y])
    ,!
    .
    
performActions([]).
performActions([Action|Tail]) :- 
    performAction(Action)
    , performActions(Tail)
    .   

performAction(Action) :-
    (Action=moveforward -> agentActualMovefwd)
    ; (Action=turnleft -> hunterActualTurnleft)
    ; (Action=turnright -> hunterActualTurnright)
    ; (Action=shoot -> hunterActualShoot)
    ; (Action=pickup -> hunterActualPickup)
    .

% relocate agent on the map - agent now loses all relative knowledge that it has gained thus far
% delete all stored data that hunter has collected
reborn :-
    retractall(hunter(_,_,_)),
    retractall(visited(_,_)),

    retractall(stench(_,_)),
    retractall(tingle(_,_)),
    retractall(wall(_,_)),
    retractall(possibleWumpus(_,_)),
    retractall(possibleConfundus(_,_)),

    assertz(hunter(1,1,rnorth)),
    assertz(visited(1,1)).

% move the agent forward by one cell.
agentActualMovefwd :-
    % get coords and directions as args (X,Y,D)
    hunter(X,Y,D) ->

    %  get new location after moving forward.
    getForwardRoom([X,Y,D], [X1,Y1]) ->

    % adds visited coords
    assertz(visited(X1,Y1)) ->
    % edit hunter coords in db
    edithunter(X1,Y1,D).

hunterActualTurnleft :- 
    % get coords and directions as args (X,Y,D)
    hunter(X,Y,D),
    leftof(D,D1),
    format('Turned left from ~w to ~w~n', [D, D1]),
    edithunter(X,Y,D1).

hunterActualTurnright :- 
    % get coords and directions as args (X,Y,D)
    hunter(X,Y,D),
    rightof(D, D1),
    format('Turned right from ~w to ~w~n', [D, D1]),
    edithunter(X,Y,D1).

hunterActualShoot :-
    hasarrow,
    write('Hunter shot arrow!'),
    assertz(hasarrow(false)).
    
% pickup a gold coin - no validation required because glitter only detected when coin in same square as agent
hunterActualPickup:-
    addGoldCoin.

% deprecated version of explore - explore now computes the next set of actions to undertake
% explore(L) :- 
%     % Take first item from list and store remainder in Ls
%     [Action|Ls] = L,
%     % check if action is one of a few options and executes the action
%     (
%         (
%         (Action=movefwd -> movefwd)
%         ; (Action=turnleft -> turnleft)
%         ; (Action=turnright -> turnright)
%         ; (Action=shoot -> shoot)

%     % continue exploring if above is true, otherwise print the action that was not valid
%     % check action list is not empty, terminate otherwise
%         ) -> (Ls=[] -> true; explore(Ls))
%             ; write(Action), write(' is not a valid action'), false
%     ).
    
% alias for hunter, since current/3 is required by specification but hunter/3 was written before that
current(X,Y,D) :-
    hunter(X,Y,D).

wumpus(X,Y) :- possibleWumpus(X,Y).
confundus(X,Y) :- possibleConfundus(X,Y).


% utility function to evaluate if hasarrow is true
hasarrow :- hasarrow(true).

% prints out current relative coordinates of hunter.
hunter :-
    !,hunter(X,Y,D),
    hasarrow(ARROW_BOOL),
    !,
    format('RX, RY: (~w, ~w)~nDirection:~w~nHas Arrow:~w~n', [X,Y,D, ARROW_BOOL]),
    !.

% db utility function - save hunter coords 
% remove previous hunter coords from db, and adds new one.
edithunter(X,Y,D) :-
    retractall(hunter(_,_,_)),
    assertz(hunter(X,Y,D)),
    !,hunter,!.

leftof(D, D1) :-
    (D = rnorth, D1=rwest);(D = rwest, D1=rsouth);(D = rsouth, D1=reast);(D = reast, D1=rnorth).

rightof(D, D1) :-
    (D = rnorth, D1=reast);(D = reast, D1=rsouth);(D = rsouth, D1=rwest);(D = rwest, D1=rnorth).
    
getForwardRoom([X0,Y0,D0], [XN,YN]) :-
    (D0 = rnorth, XN is X0, YN is Y0+1);
    (D0 = reast, XN is X0+1, YN is Y0);
    (D0 = rsouth, XN is X0, YN is Y0-1);
    (D0 = rwest, XN is X0-1, YN is Y0).

getAdjacentRooms([X0, Y0], ListOfRoomCoords) :-
    XL is X0-1,
    XR is X0+1,
    YD is Y0-1,
    YU is Y0+1,
    append([[XL,Y0], [XR,Y0], [X0,YU], [X0,YD]],[],ListOfRoomCoords).


% filterUsingPredicate(L, Predicate, OutputList) :-
%     maplist(appendIfPredicate, L, Predicate, OutputList)
%     maplist(call, )
%     .

% appendIfPredicate(Item, Predicate, OutputList) :- 
%     Predicate -> append(Item, OutputList, OutputList).

% f(I) :- I > 1.

% example code - dont use the function, but see how its implemented and use that instead
% taking in one list item and 2 Variables, setting the variables to the first item of the list and the remaining list to the second var.
listpop(L, FirstItem, RemainingList) :-
    [FirstItem|RemainingList] = L.

% conditionalExecuteAndContinue:-
    % , Predicate -> ... ; elsestatement, true
    % , ...
    % .