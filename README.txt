#README

short description of both your search approach and the
heuristic you have implemented, along with the names of both teammates and any other useful
information.


Check function checks to make sure we never have one of tools, ore, coal, or wood
It also makes sure we do not have too much of certain items as well. We will never
have more than 8 sticks, for example. The check function will also negate any recipes
if the recipe requires items that need a certain tool to acquire. An example,
if we do not have a wooden pickaxe, then it is impossible for us the fulfill a recipe that asks 
for coal as a requirement.

The heuristic will return infinity when the state has more than one tool, as does the checker.
We also return infinity when the state requires or produces an item that is above or max.

Our search uses A* and depends on the heuristic to return either zero
or infinity to help guide the path to the goal before the alotted time.
