from pyswip import Prolog

if (__name__ == "__main__"):
    prolog = Prolog()
    prolog.consult("prolog_agent/agent.pl")

    for soln in prolog.query("explore(L)"):
        #print(soln["L"])
        print(soln)