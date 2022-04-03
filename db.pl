% delete all references to these values, which are variable we will use
:- abolish(hunter/3).
:- abolish(visited/2).

% tells the compiler that these are variables which will change at runtime
:- dynamic([
    hunter/3,
    visited/2,
    gold_coords/2,
    no_of_coins/1, 
    hasarrow/1
]).

% import these .pl files
:- [walls].
:- [driver].

hunterAlive(true).
wumpusAlive(true).

% instantiate the relative coords and facing of the agent.
% at any time there should only be one value of hunter(x,y,d) -- use edithunter to modify hunter coords
hunter(1,1, rnorth).

visited(1,1).
hasarrow(true).
hasgold(false).
iscounfounded(false).

% TODO - Fill in
% wumpus(X,Y) :- true.
% confundus(X,Y) :- true.
% tingle(X,Y) :- true.
% stench(X,Y) :- true.

% delete all stored data that hunter has collected
reborn :-
    retractall(hunter(_,_,_)),
    retractall(visited(_,_)),

    assertz(hunter(1,1,n)),
    assertz(visited(1,1)).

% pickup might be removed from inside here and moved into agent at some later stage
glitter(X,Y):- 
    gold_coords(X,Y),
    write("GOLD FOUND"),nl,
    % if gold exists, pick it up and set hasgold to true
    pickup(X,Y).

pickup(X,Y):-
    retract(gold_coords(X,Y)),
    assertz(hasgold(true))
    % TODO check if we need to keep track of the number of coins we have
    .

movefwd :-
    % get coords and directions as args (X,Y,D)
    hunter(X,Y,D),

    %  get new location after moving forward.
    getForwardRoom([X,Y,D], [X1,Y1,D1]),

    %  assert that there is no wall in front of the hunter.
    \+(
        wall(X1,Y1) -> (write('Bumped into wall'), true)
    ),

    % adds visited coords
    assertz(visited(X1,Y1)),
    % edit hunter coords in db
    edithunter(X1,Y1,D1),
    % check if gold exists and if exists, retrieves it.
    check_gold_coords(X1, X2).

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

shoot :-
    hasarrow,
    write('Hunter shot arrow!'),
    assertz(hasarrow(false)).

explore(L) :- 
    % Take first item from list and store remainder in Ls
    [Action|Ls] = L,
    % check if action is one of a few options and executes the action
    (
        (Action=movefwd -> movefwd);
        (Action=turnleft -> turnleft);
        (Action=turnright -> turnright);
        (Action=shoot -> shoot)
        % (Action=pickup -> pickup);

    % continue exploring if above is true, otherwise print the action that was not valid
    % check action list is not empty, terminate otherwise
    ) -> (Ls=[] -> true; explore(Ls)); write(Action),write(' is not a valid action'),false.
    
isSafeMove :- true.


% check if wumpus exists in the current row/column we are shooting from, based on direction
wumpusdestruction(X,Y,D):-
    %TODO must check wumpus only in front, instead of entire row
    %TODO add functionality to retract wumpus once found
    (D = rnorth, wumpus_coords(X, _)),
    (D = rsouth, wumpus_coords(X, _)),
    (D = reast, wumpus_coords(_, Y)),
    (D = rwest, wumpus_coords(_, Y)).

% alias for hunter, since current/3 is required by specification but hunter/3 was written before that
current(X,Y,D) :-
    hunter(X,Y,D).

% utility function to evaluate if hasarrow is true
hasarrow :- hasarrow(true).

% prints out current relative coordinates of hunter.
hunter :-
    !,hunter(X,Y,D),
    hasarrow(ARROW_BOOL),
    !,
    format('RX, RY: (~w, ~w)~nDirection:~w~nArrow:~w~n', [X,Y,D, ARROW_BOOL]),
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
    
getForwardRoom([X0,Y0,D0], [XN,YN, D0]) :-
    (D0 = rnorth, XN is X0, YN is Y0+1);
    (D0 = reast, XN is X0+1, YN is Y0);
    (D0 = rsouth, XN is X0, YN is Y0-1);
    (D0 = rwest, XN is X0-1, YN is Y0).

% utility function taking in one list item and 2 Variables, setting the variables to the first item of the list and the remaining list to the second var.
listpop(L, FirstItem, RemainingList) :-
    [FirstItem|RemainingList] = L.