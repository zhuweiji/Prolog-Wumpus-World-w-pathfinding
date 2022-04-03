:- abolish(hunter/3).

:- dynamic([
    hunter/3,
    visited/2,
    gold_coords/2,
    no_of_coins/1, 
    hasarrow/1
]).

:- [walls].
:- [driver].

hunterAlive(true).
wumpusAlive(true).

% instantiate the relative coords and facing of the agent.
hunter(1,1, rnorth).
visited(1,1).
hasarrow(true).
hasgold(false).
iscounfounded(false).

% TODO - Fill in
wumpus(X,Y) :- true.
confundus(X,Y) :- true.
tingle(X,Y) :- true.
glitter(X,Y) :- true.
stench(X,Y) :- true.


reborn :-
    retractall(hunter(_,_,_)),
    retractall(visited(_,_)),

    assertz(hunter(1,1,n)),
    assertz(visited(1,1)).


movefwd :-
    % get coords and directions as args (X,Y,D)
    hunter(X,Y,D),

    %  get new location after moving forward.
    getForwardRoom([X,Y,D], [X1,Y1,D1]),

    %  assert that there is no wall in front of the hunter.
    \+ wall(X1,Y1),

    % adds visited coords
    assertz(visited(X1,Y1)),
    % edit hunter coords in db
    edithunter(X1,Y1,D1),
    % check if gold exists and if exists, retrieves it.
    check_gold_coords(X1, X2).

check_gold_coords(X,Y):- 
    gold_coords(X,Y),
    write("GOLD FOUND"),nl,
    % if gold exists, pick it up and set hasgold to true
    pick_up_gold(X,Y).

pick_up_gold(X,Y):-
    retract(gold_coords(X,Y)),
    assertz(hasgold(true))
    % TODO check if we need to keep track of the number of coins we have
    .

turnleft :- 
    % get coords and directions as args (X,Y,D)
    hunter(X,Y,D),
    leftof(D,D1),
    format('Turned left from ~w to ~w~n', [D, D1]),
    edithunter(X,Y,D1).

turnright :- 
    % get coords and directions as args (X,Y,D)
    hunter(X,Y,D),
    rightof(D, D1),
    format('Turned right from ~w to ~w~n', [D, D1]),
    edithunter(X,Y,D1).

current(X,Y,D) :-
    hunter(X,Y,D).

hasarrow :- hasarrow(true).

shoot :-
    hasarrow,
    write('Hunter shot arrow!'),
    assertz(hasarrow(false)),
    hunter(X,Y,D),
    write(X).

% check if wumpus exists in the current row/column we are shooting from, based on direction
wumpusdestruction(X,Y,D):-
    %TODO must check wumpus only in front, instead of entire row
    %TODO add functionality to retract wumpus once found
    (D = rnorth, wumpus_coords(X, _)),
    (D = rsouth, wumpus_coords(X, _)),
    (D = reast, wumpus_coords(_, Y)),
    (D = rwest, wumpus_coords(_, Y)).

% db utility function - save hunter coords 
% remove previous hunter coords from db, and adds new one.
edithunter(X,Y,D) :-
    retractall(hunter(_,_,_)),
    assertz(hunter(X,Y,D)),
    !,hunter,!.
    
% prints out current relative coordinates of hunter.
hunter :-
    !,hunter(X,Y,D),
    hasarrow(ARROW_BOOL),
    !,
    format('RX, RY: (~w, ~w)~nDirection:~w~nArrow:~w', [X,Y,D, ARROW_BOOL]),
    !.

printreasoned(X,Y) :- 
    (iscounfounded(true), write('%')) -> write('.').



leftof(D, D1) :-
    (D = rnorth, D1=rwest);
    (D = rwest, D1=rsouth);
    (D = rsouth, D1=reast);
    (D = reast, D1=rnorth).

rightof(D, D1) :-
    (D = rnorth, D1=reast);
    (D = reast, D1=rsouth);
    (D = rsouth, D1=rwest);
    (D = rwest, D1=rnorth).
    
getForwardRoom([X0,Y0,D0], [XN,YN, D0]) :-
    (D0 = rnorth, XN is X0, YN is Y0+1);
    (D0 = reast, XN is X0+1, YN is Y0);
    (D0 = rsouth, XN is X0, YN is Y0-1);
    (D0 = rwest, XN is X0-1, YN is Y0).