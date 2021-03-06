import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush
from math import inf

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


    #for x in rule['Produces']:
         #product = x

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].

        if need == {}:
            return True
        
        one_max = ["bench","furnace","cart", "iron_axe", "iron_pickaxe", "stone_axe", "stone_pickaxe", "wooden_axe", "wooden_pickaxe","coal","ore", "wood"]
        max_items = {"stick":8,"ingot":6,"plank":4,"cobble":8,}

        #hands, what you cannot make.
        level_0 = { "cart":1, "furnace":1, "iron_axe":1, "iron_pickaxe":1, "stone_axe":1, "stone_pickaxe":1, "ore":1, "coal":1, "cobble":1,"ingot":1,"rail":1}
        #wooden pickaxe, what you cannot make
        level_1 = { "cart":1, "furnace":1, "iron_axe":1, "iron_pickaxe":1, "stone_axe":1, "stone_pickaxe":1, "wooden_axe":1,  "ore":1, "coal":1,"rail":1}
        #stone pickaxe, what you cannot make
        level_2 = { "cart":1, "iron_axe":1, "iron_pickaxe":1,"rail":1}
        #iron pickaxe can make everything
        for item in state:
            if state[item] > 1 and item in one_max:
                #if item != "wood":
                    #print(rule)
                    #rule['Time'] = 5
                return False
            else:
                if item in max_items and state[item] > max_items[item]:
                    return False
        #print(state)
        #if state["wooden_pickaxe"] is 1:
            #print("-------------- wood pick")


        if state["wooden_pickaxe"] is not 1:
            for item in need:
                if item in level_0:
                    return False

        elif state["wooden_pickaxe"] is 1 and state["stone_pickaxe"] is not 1:
            for item in need:
                if item in level_1:
                    return False
        elif state["stone_pickaxe"] is 1 and state["iron_pickaxe"] is not 1:
            for item in need:
                if item in level_2:
                    return False

        bool_buddy = False
 
        # for each item we need, check if we have it in this state; if we don't, we can't use this recipe
        for needed_item in need:
            if needed_item in state:
                if state[needed_item] < need[needed_item]:
                    bool_buddy = False
                    break
                else:
                    rule['Time'] = 5
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


    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        for key in goal:
            goal_key = key
            goal_num = goal[key]

            if goal_key in state:
                if goal_num > state[goal_key]:
                    return False

        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)



def heuristic(state,recipe_name):
    # Implement your heuristic here!
    #print(recipe_name)


    need = {}
    if 'Requires' in Crafting['Recipes'][recipe_name]:
        need.update(Crafting['Recipes'][recipe_name]['Requires'])
    if 'Produces' in Crafting['Recipes'][recipe_name]:
        need.update(Crafting['Recipes'][recipe_name]['Produces'])



    one_max = ["bench","furnace","cart", "iron_axe", "iron_pickaxe", "stone_axe", "stone_pickaxe", "wooden_axe", "wooden_pickaxe","coal","ore", "wood"]
    max_items = {"stick":8,"ingot":6,"plank":4,"cobble":8,}

    for item in state:
        if state[item] > 1 and item in one_max:
            return inf
        else:
            if item in max_items and state[item] > max_items[item]:
                return inf
    return 0

def search(graph, state, is_goal, limit, heuristic):
    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state

    # should be deletable
    path = [('initial state', 'do a thing')]
    visited = 0
    initial_state = state.copy()

    while time() - start_time < limit:
        # distance from initial state: key = node, value = distance
        dist = {initial_state: 0}
        # previous node in the list: key = node, value = parent action
        prev = {initial_state: (None, None)}

        # heap: [(priority, current_state)]
        heap = [(0, initial_state)]

        while heap:
            current_priority, current_node = heappop(heap)
            visited += 1

            if is_goal(current_node):
                path = [(current_node, 'Complete!')]   # edit so contains tuple of (current_node, action)
                previous_node, previous_action = prev[current_node]
                while previous_action is not None:
                    path.insert(0, (previous_node, previous_action))
                    previous_node, previous_action = prev[previous_node]
                break

            else:
                for action_name, next_state, cost in graph(current_node.copy()):
                    path_cost = dist[current_node] + cost  # do math here to calculate weight of actions or something
                    est_to_end = heuristic(next_state,action_name)
                    total_estimate = path_cost + est_to_end

                    if next_state not in dist or path_cost < dist[next_state]:
                        prev[next_state] = (current_node, action_name)
                        dist[next_state] = path_cost
                        heappush(heap, (total_estimate, next_state)) # instead of option, push option.effect(state)

            if time() - start_time > limit:
                break

        print('Compute time: ', time() - start_time, 'seconds.')
        print('Goal cost: ', dist[current_node], '.')
        print('States visited: ', visited, '.')
        return path

    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    print('States visited: ', visited, '.')
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
    print('Goal:', Crafting['Goal'])

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

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 30, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t', state)
            print(action)
