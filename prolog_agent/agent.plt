:- begin_tests(agent).
:- include(agent).

% each dynamic call is only applicable to its own file.
:- dynamic([
    hunter/3,
    visited/2,
    stench/2,
    tingle/2,
    wall/2,

    possibleWampus/2,

    hasarrow/1,
    numGoldCoins/1
]).

test(reborn) :-
    reborn
    , assertion(hunter(1,1, rnorth))
    .

test(checkWumpusPerceptBehavior) :-
    addStenchKnowledge([100,100])
    , assertion(possibleWumpus(100,101))
    , assertion(possibleWumpus(101,100))
    , assertion(possibleWumpus(99,100))
    , assertion(possibleWumpus(100,99))
    .

test(checkTinglePerceptBehavior) :-
    addTingleKnowledge([100,100])
    , assertion(possibleConfundus(100,101))
    , assertion(possibleConfundus(101,100))
    , assertion(possibleConfundus(99,100))
    , assertion(possibleConfundus(100,99))
    .

test(performActions) :- 
    performActions([movefwd, turnleft, movefwd])
    , hunter(X,Y,D)
    , assertion(X is 0)
    , assertion(Y is 2)
    , reborn
    .


test(movement) :-
    reborn
    , move([movefwd], off, off, off, off, off, off)
    , hunter(X,Y,D)
    , format('~w/~w~n', [X,Y])

    , assertion(X is 1)
    , assertion(Y is 2)

    % %%%% function reference move(ListOfActions, Confounded, Stench, Tingle, Glitter, Bump, Scream) :-
    , move([movefwd], off, on, off, off, off, off)
    , hunter(X0,Y0,D0)

    % , assertion(X1 is 1)
    % , assertion(Y1 is 3)
    .

:- end_tests(agent).

% all of the below statements must be true.
% forall(
% % test hunter initialized properly.
% hunter(1,1, rnorth)
% , addPossibleWampus([[100,100]])
% , possibleWampus(100,100)
% , not(possibleWampus(100,101))
% , not(possibleWampus(100,100))
% ).

