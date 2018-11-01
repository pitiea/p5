import json
import math
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush


Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    need = {}

    if 'Requires' in rule:
        need.update(rule['Requires'])
    if 'Consumes' in rule:
        need.update(rule['Consumes'])


    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].

        if need == {}:
            return True

        bool_buddy = False

        for needed_item in need:
            if needed_item in state:
                if state[needed_item] < need[needed_item]:
                    bool_buddy = False
                    break
                bool_buddy = True
            else:
                break

        return bool_buddy

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    products = rule['Produces']
    cost = {}
    if 'Consumes' in rule:
        cost = rule['Consumes']

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        next_state = state.copy()
        for item in products:
            next_state[item] += products[item]
        for item in cost:
            next_state[item] -= cost[item]

        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    for key in goal:
        goal_key = key
        goal_num = goal[key]

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.

        if goal_key in state:
            if goal_num == state[goal_key]:
                return True

        return False

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            #print("state in graph: ", state)
            #print("r: ", r)
            yield (r.name, r.effect(state), r.cost)
        else:#if the rule in not in the state, meaning it is not valid, set its cost to infinity
        	inf_cost = math.inf #change cost of invalid path to infinity
        	#state[r]
        	#change the invalid recipe time = inf_cost
        	#set the rule to have the infinite cost

def heuristic(state):
    # Implement your heuristic here!

    #can also look at just the action, and see how the action rekates to the goal.
    
    # loop through all the "requires", and if we already have one in state, return infinity. Example, if we have a pickaxe, we dont need another

    #can also check if they produce the same thing, and choose the lowest cost. setting the 

    return 0


def search(graph, state, is_goal, limit, heuristic):
    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state

    # should be deletable
    path = [('initial state', 'do a thing')]

    initial_state = state.copy()
    #print("initial_state: ", initial_state)

    while time() - start_time < limit:
        # distance from initial state: key = node, value = distance
        dist = {initial_state: 0}
        # previous node in the list: key = node, value = parent action
        prev = {initial_state: None}

        # heap: [(priority, current_state)]
        heap = [(0, initial_state)]

        while heap:
            current_priority, current_node = heappop(heap)

            if is_goal(current_node):
                path = [(current_node, None)]   # edit so contains tuple of (current_node, action)
                previous_node = prev[current_node]
                while previous_node is not None:
                    path.insert(0, previous_node)
                    previous_node = prev[previous_node]
                break

            else:
                #print("current_node before graph but after isgoal: ", current_node)
                for action_name, next_state, cost in graph(current_node.copy()):
                    #print("option: ", action_name)
                    #print("current_node: ", current_node)
                    #print("dist: ", dist)
                    path_cost = dist[current_node] + cost  # do math here to calculate weight of actions or something
                    est_to_end = heuristic(state)
                    total_estimate = path_cost + est_to_end

                    if next_state not in dist or path_cost < dist[next_state]:
                        prev[next_state] = (current_node, action_name)
                        dist[next_state] = path_cost
                        heappush(heap, (total_estimate, next_state)) # instead of option, push option.effect(state)

        return path

    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None


if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    #print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    #print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    #print('Goal:', Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    # print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    # state = State()
    state.update(Crafting['Initial'])

    x = 1
    y = True
    if x == y:
        print("oh good")
    else:
        print("oh no")

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 50, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t', state)
            print(action)
