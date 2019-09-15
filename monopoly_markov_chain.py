"""
This program uses a Markov chain to determine how often each space on a Monopoly board is landed on.

The program constructs a transition matrix and raises it to a high power to get a steady-state matrix, which shows
the overall probability of landing on each space.

The leave_jail_immediately variable determines if the player will immediately pay to leave jail, or if they will
attempt to roll doubles to get out of jail for free.
"""

import numpy as np
import itertools


leave_jail_immediately = False


def add_rolls():
    """Adds rolls to the matrix, ignoring special movement of spaces like Go To Jail"""
    for current_space in range(40):
        for roll, probability in roll_no_doubles.items():
            new_space = add_spaces(current_space, roll)
            for doubles_state in doubles_states:
                the_array[doubles_state(current_space)][new_space] += probability
        for roll, probability in roll_doubles.items():
            new_space = add_spaces(current_space, roll)
            the_array[no_doubles(current_space)][one_doubles(new_space)] += probability
            the_array[one_doubles(current_space)][two_doubles(new_space)] += probability
            the_array[two_doubles(current_space)][jail_dict[0]] += probability


def leave_jail():
    """Adds the behavior of the three jail sates to the matrix"""
    if leave_jail_immediately:
        the_array[jail_dict[0]] = the_array[no_doubles(space_dict["Visiting Jail"])]
    else:
        for jail_state in jail_dict.values():
            # If non-doubles are rolled, increments the jail state if in state 0 or 1, or moves normally if in state 2
            if jail_state in (jail_dict[0], jail_dict[1]):
                the_array[jail_state][jail_state + 1] += sum(roll_no_doubles.values())
            else:
                for roll, probability in roll_no_doubles.items():
                    the_array[jail_state][add_spaces(space_dict["Visiting Jail"], roll)] += probability
            # If doubles are rolled, moves the number of spaces shown from Visiting Jail on the no doubles state
            for roll, probability in roll_doubles.items():
                the_array[jail_state][no_doubles(add_spaces(space_dict["Visiting Jail"], roll))] += probability


def add_chance_and_community_chest():
    """Adds Chance and Community Chest behavior to the matrix"""
    def find_nearest_utility(space):
        space %= 40
        if space_dict["Electric Company"] <= space < space_dict["Water Works"]:
            return space_dict["Water Works"]
        else:
            return space_dict["Electric Company"]

    def find_nearest_railroad(space):
        space %= 40
        railroads = (space_dict["Reading Railroad"], space_dict["Pennsylvania Railroad"], space_dict["B&O Railroad"],
                     space_dict["Short Line"])
        for i in range(3):
            if railroads[i] <= space < railroads[i + 1]:
                return railroads[i + 1]
        else:
            return space_dict["Reading Railroad"]

    card_probability = 1 / 16
    chance_spaces = (space_dict["Chance 1"], space_dict["Chance 2"], space_dict["Chance 3"])
    community_chest_spaces = (space_dict["Community Chest 1"], space_dict["Community Chest 2"],
                              space_dict["Community Chest 3"])

    for space, doubles_state in itertools.product(range(120), doubles_states):

        # Adds Chance behavior
        for chance_space in chance_spaces:
            # Finds probability of landing on the current chance space and then drawing a particular chance card
            net_probability = the_array[space][doubles_state(chance_space)] * card_probability

            for chance_card in (space_dict["Go"], space_dict["Illinois Avenue"], space_dict["St. Charles Place"],
                                find_nearest_utility(chance_space), find_nearest_railroad(chance_space),
                                find_nearest_railroad(chance_space), (chance_space - 3) % 40,
                                space_dict["Reading Railroad"], space_dict["Boardwalk"]):

                # Moves net_probability from ending the turn on the chance space to ending where the card puts you
                the_array[space][doubles_state(chance_card)] += net_probability
                the_array[space][doubles_state(chance_space)] -= net_probability
            # Going to jail is handled separately because it goes to the same state regardless of current doubles state
            the_array[space][jail_dict[0]] += net_probability
            the_array[space][doubles_state(chance_space)] -= net_probability

        # Adds Community Chest behavior
        for community_chest_space in community_chest_spaces:
            net_probability = the_array[space][doubles_state(community_chest_space)] * card_probability

            the_array[space][doubles_state(space_dict["Go"])] += net_probability
            the_array[space][doubles_state(community_chest_space)] -= net_probability

            the_array[space][jail_dict[0]] += net_probability
            the_array[space][doubles_state(community_chest_space)] -= net_probability


def go_to_jail_space():
    """Makes the 'Go To Jail' space actually send you to jail"""
    jail_doubles_states = [doubles_state(space_dict["Go To Jail"]) for doubles_state in doubles_states]
    for space, doubles_state, jail_doubles_state in itertools.product(range(40), doubles_states, jail_doubles_states):
        the_array[doubles_state(space)][jail_dict[0]] += the_array[doubles_state(space)][jail_doubles_state]
        the_array[doubles_state(space)][jail_doubles_state] = 0


def print_results():
    """Prints the results of the computation"""
    results = {}
    # Adds the three doubles states for each non-jail space together and puts the result in the results dict
    for space_name, space_num in space_dict.items():
        results.setdefault(space_name, 0)
        for doubles_state in doubles_states:
            results[space_name] += the_array[0][doubles_state(space_num)]
        
    # Adds the three in-jail states and put them in the dict
    results["In Jail"] = sum(the_array[0][jail_dict[0]:jail_dict[2] + 1])

    # Print the results in descending order
    width = 30
    print("|" + "Results".center(width, "=") + "|")
    for space, probability in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"|" + space.ljust(width-6, ".") + str(round(probability, 4)).ljust(6, "0") + "|")
    print("|" + "=" * width + "|")


def add_spaces(*nums: int) -> int:
    return sum(nums) % 40


# These three functions, while not strictly necessary, improve readability elsewhere in the program
def no_doubles(space:int) -> int:
    return space


def one_doubles(space:int) -> int:
    return space + 40


def two_doubles(space:int) -> int:
    return space + 80


doubles_states = (no_doubles, one_doubles, two_doubles)

# Builds a dictionary of space names and their respective integer values for code readability
spaces = ["Go", "Mediterranean Avenue", "Community Chest 1", "Baltic Avenue",
          "Income Tax", "Reading Railroad", "Oriental Avenue", "Chance 1",
          "Vermont Avenue", "Connecticut Avenue", "Visiting Jail", "St. Charles Place",
          "Electric Company", "States Avenue", "Virginia Avenue", "Pennsylvania Railroad",
          "St. James Place", "Community Chest 2", "Tennessee Avenue", "New York Avenue",
          "Free Parking", "Kentucky Avenue", "Chance 2", "Indiana Avenue", "Illinois Avenue",
          "B&O Railroad", "Atlantic Avenue", "Ventnor Avenue", "Water Works", "Marvin Gardens",
          "Go To Jail", "Pacific Avenue", "North Carolina Avenue", "Community Chest 3",
          "Pennsylvania Avenue", "Short Line", "Chance 3", "Park Place", "Luxury Tax", "Boardwalk"]
space_dict = dict(zip(spaces, list(range(40))))

# Builds a separate dictionary for the three In Jail states, which are usually handled separately
jail_dict = {0: 120, 1: 121, 2: 122}

the_array = np.zeros((123, 123))

# Calculates the probability of every possible roll.  Used by both add_rolls and roll_to_leave_jail
roll_no_doubles = {}
roll_doubles = {}
for die_1, die_2 in itertools.product(range(1, 7), range(1, 7)):
    total = die_1 + die_2
    if die_1 != die_2:
        roll_no_doubles.setdefault(total, 0)
        roll_no_doubles[total] += 1 / 36
    else:
        roll_doubles.setdefault(total, 0)
        roll_doubles[total] += 1 / 36

# Runs each of the functions to add space behavior to the array
add_rolls()
leave_jail()
add_chance_and_community_chest()
go_to_jail_space()

# Raises the array to a large power
for i in range(30):
    the_array = np.matmul(the_array, the_array)

# Prints the results
print_results()
