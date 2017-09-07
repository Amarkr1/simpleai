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
        return wrong + missing
    
    

problem = HelloProblem(initial_state='HALL')
result = astar(problem)
#result = breadth_first(problem)
#result = depth_first(problem)

print(result.state)
print(result.path())