#test code from the web
from simpleai.search import SearchProblem, astar,breadth_first,depth_first

GOAL = 'HELLO WORLD'


class HelloProblem(SearchProblem):
    def actions(self, state):
        if len(state) < len(GOAL):
            return list(' ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        else:
            return []

    def result(self, state, action):
        return state + action

    def is_goal(self, state):
        return state == GOAL

    def heuristic(self, state):
        # how far are we from the goal?
        wrong = sum([1 if state[i] != GOAL[i] else 0
                    for i in range(len(state))])
        
        missing = len(GOAL) - len(state)
        #print(wrong+missing)
        return wrong + missing
    
def commonString(string1, string2):
    answer = ""
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = ""
        for j in range(len2):
            if (i + j < len1 and string1[i + j] == string2[j]):
                match += string2[j]
            else:
                if (len(match) > len(answer)): answer = match
                match = ""
    return answer 

initial_state='HELLO wORLD'
modified_state = commonString(initial_state,GOAL)
problem = HelloProblem(initial_state = modified_state)
result = astar(problem)
#result = breadth_first(problem)
#result = depth_first(problem)
print("Initial state: ",initial_state)
print("Modified state: ",modified_state)
print("Goal: ",result.state)
print(result.path())