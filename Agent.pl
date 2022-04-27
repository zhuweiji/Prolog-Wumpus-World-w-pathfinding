% delete all references to these values, which are variable we will use
:- abolish(reposition/1).

:- abolish(hunter/3).
:- abolish(visited/2).
:- abolish(stench/2).
:- abolish(tingle/2).
:- abolish(wall/2).
:- abolish(safe/2).
:- abolish(glitter/1).
:- abolish(glitter/2).

:- abolish(possibleWumpus/2).
:- abolish(possibleConfundus/2).
:- abolish(wumpusAlive/1).
:- abolish(hasarrow/0).
:- abolish(numGoldCoins/1).


:- abolish(justbumped/1).
:- abolish(justscreamed/1).

:- abolish(returnToStart/1).

% tells the compiler that these are variables which will change at runtime
:- dynamic([
    reposition/1,
    hunter/3,
    visited/2,
    stench/2,
    tingle/2,
    wall/2,
    safe/2,
    glitter/1,
    glitter/2,

    possibleWumpus/2,
    possibleConfundus/2,
    wumpusAlive/1,
    hasarrow/0,
    numGoldCoins/1,
    justbumped/1,
    justscreamed/1,
    returnToStart/1
]).


% ================== FACTS - This section contains the knowledge that the agent starts with ===========================

% facts that will always be true - even if the agent teleports to another location
hunterAlive(true).

% instantiate the relative coords and facing of the agent.
% at any time there should only be one value of hunter(x,y,d) -- use edithunter to modify hunter coords
% reborn.
hunter(0,0, rnorth).
visited(0,0).
safe(0,0).

% facts that may change over time.
wumpusAlive(true).
hasarrow.
numGoldCoins(0).
iscounfounded(false).
glitter(false).

justbumped(false).
justscreamed(false).

returnToStart(false).
% ======================================= END FACTS ========================================================================

% ===================== PERCEPTS - Implements the knowledge the agent will gain as it traverses the map =======
% PART ONE - Use existing knowledge of the world to determine next moves
% 1. find a new room to move to that is not visited and is safe
% 2. find a a set of safe moves to move to that new room

% finds a set of moves to a safe,unvisited room
explore(L) :-
    (returnToStart(true), logMessage('Agent has completed its exploration of the game space.'), L=[])
    ;(
    hunter(X,Y,D)
    , retractall(justbumped(true)), retractall(justscreamed(true))
    , assertz(justbumped(false)), assertz(justscreamed(false))

    % find some safe moves to get to a new safe unvisited room
    , (simFindMovesToRoom([s(room(X,Y), D, [])], DestinationRoom, [], TL, 100)
        -> (logMessage('Destination room: ', DestinationRoom))
        ; (
            logMessage('Could not find new rooms to explore -  Returning to relative origin.')
            , findPathToRelativeOrigin([s(room(X,Y), D, [])], [], TL, 100)
        )
    )
    
    % every 'move' is [move1,...] so output list is 2-d array. Flatten list for output
    , flatten2(TL, L)
    ).

% % wraps BFS find room function for better interface, and logs the output
% findNewRoom(room(X,Y), DestinationRoom) :-
%     checkRoomOrAddAdj([room(X,Y)], [], DestinationRoom)
%     , logMessage('Heuristic finds safe room', DestinationRoom)
%    .

% % look for a safe room recursively, adding adjacent rooms for a BFS search
% checkRoomOrAddAdj([Room|ListOfOtherRooms], CheckedRooms, DestinationRoom) :-
%     (
%         \+ member(Room, CheckedRooms)
%         , append([Room], CheckedRooms, NewCheckedRooms)
%         , (
%             (
%                 \+ roomIsDangerous(Room)
%                 , room(X,Y) = Room
%                 , \+ visited(X,Y)
%                 , DestinationRoom = Room
%             )
%             ; (
%                 % condition - if list of rooms is within bounds expand its neighbours
%                 (withinBounds(Room) -> 
%                     (getAdjacentRooms(Room, L)
%                     , append(ListOfOtherRooms, L, NewListOfOtherRooms)
%                     , remove_duplicates(NewListOfOtherRooms, UniqueListOfRooms)
%                     , write(UniqueListOfRooms), nl
%                     ), checkRoomOrAddAdj(UniqueListOfRooms, NewCheckedRooms, DestinationRoom)
                
%                 % just recurse
%                 ) ; checkRoomOrAddAdj(ListOfOtherRooms, NewCheckedRooms, DestinationRoom)
%             )
%         )
%     )
%     ; checkRoomOrAddAdj(ListOfOtherRooms, CheckedRooms, DestinationRoom)
%     .

roomIsDangerous(room(X,Y)) :-
    possibleWumpus(X, Y)
    ; possibleConfundus(X, Y)
    ; wall(X,Y)
    .

% BFS search for safe moves to a given room from a starting room
simFindMovesToRoom([s(CurrRoom, CurrDir, Moves)|StateTail], EndRoom, CheckedRooms, OutputMoves, Iterations) :-
%     % if current room is destination room, terminate
    ( CurrRoom = EndRoom, room(EX,EY)=EndRoom, \+visited(EX,EY),!, 
        (glitter(true) -> (logMessage('Picked up gold'), OutputMoves=[pickup|Moves]); Moves=OutputMoves))
    ;(Iterations = 0, false)
    ; (
        I0 is Iterations-1
        % find all moves that can be made from this room to another room
        , findall(
            s(NextRoom, NextDir, [Moves|Move]),
            simMakeMove(CurrRoom,CurrDir,NextRoom,NextDir, Move),
            States
        )
        % remove forward rooms to rooms which have already been explored
        , findall(State,
            (member(State, States)
            ,\+isInCheckedRoom(State, CheckedRooms)
            ),
            NewStates)        
        % , write(NewStates),nl
        , getRoomsFromState(NewStates, NewCheckedRooms)
        , append(NewCheckedRooms, CheckedRooms, FinalCheckedRooms)
        , append(StateTail, NewStates, NewStateTail)
        , simFindMovesToRoom(NewStateTail, EndRoom, FinalCheckedRooms, OutputMoves, I0)
    )
    .

% BFS search for safe moves to starting room
findPathToRelativeOrigin([s(CurrRoom, CurrDir, Moves)|StateTail], CheckedRooms, OutputMoves, Iterations) :-
%     % if current room is destination room, terminate
    (CurrRoom = room(0,0),!, retractall(returnToStart(false)), assertz(returnToStart(true)), Moves=OutputMoves)
    ;(Iterations = 0, logMessage('Could not find path back to relative origin.'))
    ; (
        I0 is Iterations-1
        % find all moves that can be made from this room to another room
        , findall(
            s(NextRoom, NextDir, [Moves|Move]),
            simMakeMove(CurrRoom,CurrDir,NextRoom,NextDir, Move),
            States
        )
        % remove forward rooms to rooms which have already been explored
        , findall(State,
            (member(State, States)
            ,\+isInCheckedRoom(State, CheckedRooms)
            ),
            NewStates)        
        , getRoomsFromState(NewStates, NewCheckedRooms)
        , append(NewCheckedRooms, CheckedRooms, FinalCheckedRooms)
        , append(StateTail, NewStates, NewStateTail)
        , findPathToRelativeOrigin(NewStateTail, FinalCheckedRooms, OutputMoves, I0)
    )
    .

getRoomsFromState([], []).
getRoomsFromState([s(Room, _, _)|T], [Room|T2]) :-
    getRoomsFromState(T, T2).

isInCheckedRoom(State, LRooms) :-
    s(room(X,Y),_,_) = State
    , member(room(X,Y), LRooms).

simMakeMove(room(X0,Y0), D0, room(FX,FY), DF, Actions) :-
    (
        (
            Actions=[moveforward] 
            , moveforward(room(X0,Y0), D0, room(X1,Y1))
            , \+ roomIsDangerous(room(X1,Y1))
            , withinBounds(room(X1,Y1))
            , D2 = D0
        )
        ; (Actions=[turnleft, moveforward], turnleft(D0,D2)
            , moveforward(room(X0,Y0), D2, room(X1,Y1))
            , \+ roomIsDangerous(room(X1,Y1))
            , withinBounds(room(X1,Y1))
            )
        ; (Actions=[turnright, moveforward], turnright(D0,D2)
        , moveforward(room(X0,Y0), D2, room(X1,Y1))
        , \+ roomIsDangerous(room(X1,Y1))
        , withinBounds(room(X1,Y1))
        )
        ; (Actions=[turnleft, turnleft, moveforward], turnleft(D0,D1), turnleft(D1,D2)
        , moveforward(room(X0,Y0), D2, room(X1,Y1))
        , \+ roomIsDangerous(room(X1,Y1))
        , withinBounds(room(X1,Y1))
        )
    ), (D2=DF, X1=FX, Y1=FY)
    .

%  PART TWO -  Execute some actions, and gain some new knowledge
% The agent actions the moves gathered, and obtains a set of percepts from the world

reposition(L):-
    L = [Confounded, Stench, Tingle, Glitter, Bump, Scream]
    , hunter(X,Y,_)
    ,!
    , usePrecepts(room(X,Y), Confounded, Stench, Tingle, Glitter, Bump, Scream)
    ,!
    , inferIfLackOfPrecepts(room(X,Y))
    ,!
    .

move(A, L) :-
    L = [Confounded, Stench, Tingle, Glitter, Bump, Scream]
    , move(A, Confounded, Stench, Tingle, Glitter, Bump, Scream).

% Execute a set of actions, moving the agent through the world. Agent is given list of percepts noticed in the new cell.
move(Action, Confounded, Stench, Tingle, Glitter, Bump, Scream) :-
    performAction(Action, Bump)
    , hunter(X,Y,_)
    ,!
    , usePrecepts(room(X,Y), Confounded, Stench, Tingle, Glitter, Bump, Scream)
    ,!
    , inferIfLackOfPrecepts(room(X,Y))
    ,!
    .

% % Executes a set of actions, updating the agent's knowledge of its location in the world
% performActions([], _).
% performActions([Action|Tail], Bump) :- 
%     performAction(Action)
%     ,
%     (Tail=[moveforward], Bump=on, true)
%     ; performActions(Tail, Bump)
%     .   

% performs a singular action
performAction(Action, Bump) :-
    (Action=moveforward -> ((\+Bump=on,agentActualMovefwd);true))
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
    retractall(safe(_,_)),


    retractall(stench(_,_)),
    retractall(tingle(_,_)),
    retractall(wall(_,_)),
    retractall(possibleWumpus(_,_)),
    retractall(possibleConfundus(_,_)),

    assertz(hunter(0,0,rnorth)),
    assertz(visited(0,0)),
    assertz(safe(0,0)).


% ACTIONS - These are utility functions that update the KBS with agent coordinates
% move the agent forward by one cell.
agentActualMovefwd :-
    % get coords and directions as args (X,Y,D)
    hunter(X,Y,D) ->
    %  get new location after moving forward.
    getForwardRoom(room(X, Y), D, room(X1,Y1)) ->
    % adds visited coords
    assertz(visited(X1,Y1)) ->
    % edit hunter coords in db
    edithunter(X1,Y1,D).

hunterActualTurnleft :- 
    % get coords and directions as args (X,Y,D)
    hunter(X,Y,D),
    leftof(D,D1),
    edithunter(X,Y,D1).

hunterActualTurnright :- 
    % get coords and directions as args (X,Y,D)
    hunter(X,Y,D),
    rightof(D, D1),
    edithunter(X,Y,D1).

hunterActualShoot :-
    hasarrow,
    logMessage('Hunter shot arrow!'),
    retractall(hasarrow).
    
% pickup a gold coin - no validation required because glitter only detected when coin in same square as agent
hunterActualPickup:-
    addGoldCoin.

% PART THREE - Use the percepts gained from the move to update the knowledge base
% f(L) :-
%     move(moveforward,off,off,off,off,off,off)
%     , move(moveforward,off,off,off,off,off,off)
%     , move(moveforward,off,off,on,off,off,off)
%     , explore(L).

% Update agent knowledge of the world with the percepts it is given
usePrecepts(room(X,Y), Confounded, Stench, Tingle, Glitter, Bump, Scream) :-
    (Confounded=on -> reborn                 ; true 
    , Stench=on -> addStenchKnowledge(room(X,Y)) ; true
    , Tingle=on -> addTingleKnowledge(room(X,Y)) ; true
    , Glitter=on -> addGoldKnowledge         ; true
    , Bump=on -> addWallKnowledge            ; true
    , Scream=on -> updateWumpusKilled        ; true
    ); true
    .

addGoldKnowledge:-
    retractall(glitter(false))
    , assertz(glitter(true))
    .

% when moving in a new cell, the knowledge that some percepts are not detected is information in itself
inferIfLackOfPrecepts(room(X,Y)) :-
    getAdjacentRooms(room(X,Y), AdjRooms)
    , verifyInformationInAdjRooms(room(X,Y), AdjRooms)
    % TODO only set safe if really is safe
    , setAllSurroundingRoomsAsSafe(AdjRooms)
    .

% safe rooms are actually not important to the agent - only that a square is not dangerous
setAllSurroundingRoomsAsSafe([]).
setAllSurroundingRoomsAsSafe([room(X,Y)|T]) :-
    assertz(safe(X,Y)), setAllSurroundingRoomsAsSafe(T).


verifyInformationInAdjRooms(_, []).
verifyInformationInAdjRooms(room(X,Y), AdjRooms) :-
    [AdjRoom|AdjRoomsTail] = AdjRooms,!
    , verifyPossibleWumpus(room(X,Y), AdjRoom),!
    , verifyPossibleConfundus(room(X,Y), AdjRoom),!
    , verifyInformationInAdjRooms(room(X,Y), AdjRoomsTail)
    .

% add fact that stench is at square, and note possible wumpus locations
addStenchKnowledge(room(X,Y)) :- 
    assertz(stench(X,Y))
    , getAdjacentRooms(room(X,Y), AdjRooms)
    ,!, addPossibleWumpus(AdjRooms).

% iterate over list of rooms - if room has not been visited then add a marker that Wumpus may be there
addPossibleWumpus([]).
addPossibleWumpus([room(X,Y)|AdjRoomsTail]) :-
    (
        ( \+ visited(X,Y), assertz(possibleWumpus(X,Y)) ) ; true
    )
    ,!, addPossibleWumpus(AdjRoomsTail),!
    .
verifyPossibleWumpus(room(OX,OY), room(AX, AY)) :-
    (
        possibleWumpus(AX, AY) ->
        (\+ stench(OX,OY) -> 
            (retractall(possibleWumpus(AX, AY))
            , logMessage('Removed possibility | Wumpus not in ', [AX, AY])) ;true
            ); true
    )
    .

% add fact that tingle is at square, and note possible portal locations
addTingleKnowledge(room(X,Y)) :- 
    assertz(tingle(X,Y))
    , getAdjacentRooms(room(X,Y), AdjRooms)
    ,!, addPossibleConfundus(AdjRooms).
% iterate over list of rooms - if room has not been visited then add a marker that portal may be there
addPossibleConfundus([room(X,Y)|AdjRoomsTail]) :-
    (
        ( \+ visited(X,Y), assertz(possibleConfundus(X,Y)) ) ; true
    )
    ,!, addPossibleConfundus(AdjRoomsTail),!
    .
verifyPossibleConfundus(room(OX,OY), room(CX, CY)) :-
    (
        possibleConfundus(CX,CY) -> 
        (\+ tingle(OX,OY) ->
            (retractall(possibleConfundus(CX, CY))
            , logMessage('Removed possibility | Confundus not in room', [CX, CY])
        ); true
        ); true
    )
    .

% add fact that wall is in front. 
addWallKnowledge:- 
    hunter(X,Y,D)
    , getForwardRoom(room(X, Y), D, room(X1,Y1))
    , assertz(wall(X1,Y1))
    , retractall(safe(X1,Y1))
    , retractall(justbumped(false))
    , assertz(justbumped(true))
    . 

addGoldCoin :-
    numGoldCoins(X),
    X1 is X+1,
    retractall(numGoldCoins(_)),
    assertz(numGoldCoins(X1)),
    retractall(glitter(true)),
    assertz(glitter(false)).

updateWumpusKilled :- 
    retractall(wumpusAlive(_))
    , retractall(possibleWumpus(_,_))
    , retractall(stench(_,_))
    , assertz(wumpusAlive(false))
    , retractall(justscreamed(false))
    , assertz(justscreamed(true))

    .

% PART FOUR - Utilities
% Possible actions that could be executed by the agent, changing relative coordinates but 
% not actually moving the agent in the world
moveforward(room(X0,Y0), D0, room(X1,Y1)) :-
    getForwardRoom(room(X0, Y0), D0, room(X1,Y1)).

turnleft(D0, D1) :-
    leftof(D0,D1).

turnright(D0, D1) :-
    rightof(D0,D1).

pickup :- 
    addGoldCoin.
    % numGoldCoins(I)
    % ,I0 is I+1
    % , retractall(numGoldCoins(_))
    % , assertz(numGoldCoins(I0))
    % , retractall(glitter(true))
    % , assertz(glitter(false))

shoot :- true.

    
% alias for hunter, since current/3 is required by specification but hunter/3 was written before that
current(X,Y,D) :-
    hunter(X,Y,D).

hasarrow(Bool) :- (hasarrow -> Bool=true ; Bool=false).

wumpus(X,Y) :- possibleWumpus(X,Y).
confundus(X,Y) :- possibleConfundus(X,Y).

% prints out current relative coordinates of hunter.
printHunter :-
    !,hunter(X,Y,D), hasarrow(ARROW_BOOL)
    , format('RX, RY: (~w, ~w)~nDirection:~w~nHas Arrow:~w~n', [X,Y,D, ARROW_BOOL]),
    !.

% db utility function - save hunter coords 
% remove previous hunter coords from db, and adds new one.
edithunter(X,Y,D) :-
    retractall(hunter(_,_,_)),
    assertz(hunter(X,Y,D)),
    !.

% Domain specific util functions
withinBounds(room(X,Y)) :-
    X < 7, Y < 7, X >= -7, Y >= -7.

leftof(D, D1) :-
    (D = rnorth, D1=rwest);(D = rwest, D1=rsouth);(D = rsouth, D1=reast);(D = reast, D1=rnorth).

rightof(D, D1) :-
    (D = rnorth, D1=reast);(D = reast, D1=rsouth);(D = rsouth, D1=rwest);(D = rwest, D1=rnorth).
    
getForwardRoom(room(X0, Y0), D0, room(XN,YN)) :-
    (D0 = rnorth, XN is X0, YN is Y0+1);
    (D0 = reast, XN is X0+1, YN is Y0);
    (D0 = rsouth, XN is X0, YN is Y0-1);
    (D0 = rwest, XN is X0-1, YN is Y0).

getAdjacentRooms(room(X0,Y0), ListOfRoomCoords) :-
    XL is X0-1,
    XR is X0+1,
    YD is Y0-1,
    YU is Y0+1,
    append([room(XL,Y0), room(XR,Y0), room(X0,YU), room(X0,YD)], [], ListOfRoomCoords).

isAdjacent(room(X,Y),room(XT,YT)) :-
    (X =:= XT, Y =:= YT+1);
    (X =:= XT, Y =:= YT-1);
    (X =:= XT+1, Y =:= YT);
    (X =:= XT-1, Y =:= YT).

% Generic prolog functions
reverse(List,Result) :-
    reverse(List,[],Result).
reverse([],ReversedList,ReversedList).
reverse([Head|Tail],RestTail,ReverseList) :-
     reverse(Tail,[Head|RestTail],ReverseList).

lastElement([H], Output) :- !,Output = H.
lastElement([_|T], Output) :- lastElement(T, Output).

flatten2([], []) :- !.
flatten2([L|Ls], FlatL) :-
    !,
    flatten2(L, NewL),
    flatten2(Ls, NewLs),
    append(NewL, NewLs, FlatL).
flatten2(L, [L]).


logMessage(Message) :-
    nl, write('Agent: '), write(Message), nl.

logMessage(Message, Vars) :-
    nl, write('Agent: '), format('~w - ~w', [Message, Vars]), nl.

remove_duplicates([], []).
remove_duplicates([Head | Tail], Result) :-
    member(Head, Tail), !,
    remove_duplicates(Tail, Result).
remove_duplicates([Head | Tail], [Head | Result]) :-
    remove_duplicates(Tail, Result).

