"""
This program runs a simulation of a player moving on a Monopoly board to determine how often each space is landed 
on.

num_turns determines the number of turns that will be simulated.
leave_jail_immediately determines if the player will pay to leave jail immediately or if they will attempt to roll
doubles to leave jail.
"""

import random

num_turns = 1000000
leave_jail_immediately = False


def take_turn():
    """Simulates the player rolling the dice and moving to the appropriate space"""
    def roll_dice():
        return [random.choice(range(1, 7)) for i in range(2)]

    def move(roll: list):
        global current_space
        current_space = (current_space + sum(roll)) % 40

    def find_nearest_utility(space):
        if space_to_num["Electric Company"] <= space < space_to_num["Water Works"]:
            return space_to_num["Water Works"]
        else:
            return space_to_num["Electric Company"]

    def find_nearest_railroad(space):
        railroads = (space_to_num["Reading Railroad"], space_to_num["Pennsylvania Railroad"],
                     space_to_num["B&O Railroad"], space_to_num["Short Line"])
        for i in range(3):
            if railroads[i] <= space < railroads[i + 1]:
                return railroads[i+1]
        else:
            return space_to_num["Reading Railroad"]

    global current_space, jail_rolls, num_doubles
    roll = roll_dice()

    # Handles rolling to leave jail
    if current_space == space_to_num["In Jail"] and not leave_jail_immediately:
        if jail_rolls == 2 or roll[0] == roll[1]:
            move(roll)
            jail_rolls = 0
        else:
            jail_rolls += 1

    # Handles rolling outside of jail or paying to leave jail immediately
    else:
        # If the player is leaving jail immediately, they are put on Visiting Jail before rolling normally
        if current_space == space_to_num["In Jail"] and leave_jail_immediately:
            current_space = space_to_num["Visiting Jail"]

        # Keeps track of doubles, sending the player to jail if they roll 3 in a row
        if roll[0] == roll[1]:
            if num_doubles == 2:
                current_space = space_to_num["In Jail"]
                num_doubles = 0
            else:
                num_doubles += 1
                move(roll)
        else:
            num_doubles = 0
            move(roll)

        # Handles landing on Chance and Community Chest spaces
        if (current_space in chance_spaces) or (current_space in community_chest_spaces):
            # Builds the appropriate deck
            if current_space in chance_spaces:
                deck = [space_to_num["Go"], space_to_num["Illinois Avenue"], space_to_num["St. Charles Place"],
                        find_nearest_utility(current_space), find_nearest_railroad(current_space),
                        find_nearest_railroad(current_space), current_space - 3, space_to_num["Reading Railroad"],
                        space_to_num["Boardwalk"], space_to_num["In Jail"]]
            else:
                deck = [space_to_num["Go"], space_to_num["In Jail"]]
            while len(deck) < 16:
                deck.append(None)

            # Chooses a card and moves to the appropriate space
            card = random.choice(deck)
            if card:
                current_space = card

        # Sends the player to jail if they land on "Go To Jail"
        elif current_space == space_to_num["Go To Jail"]:
            current_space = space_to_num["In Jail"]


def print_results():
    """ Prints the results of the simulation in an easily readable format"""
    width = 30
    print("|" + "RESULTS".center(width, "=") + "|")
    for space, probability in sorted(counter.items(), key=lambda x: x[1], reverse=True):
        print("|" + space.ljust(width - 6, ".") + str(round(probability / num_turns, 4)).ljust(6, "0") + "|")
    print("|" + "=" * width + "|")


# Builds dictionaries that convert a space's name to its integer value and vice versa
spaces = ["Go", "Mediterranean Avenue", "Community Chest 1", "Baltic Avenue",
          "Income Tax", "Reading Railroad", "Oriental Avenue", "Chance 1",
          "Vermont Avenue", "Connecticut Avenue", "Visiting Jail", "St. Charles Place",
          "Electric Company", "States Avenue", "Virginia Avenue", "Pennsylvania Railroad",
          "St. James Place", "Community Chest 2", "Tennessee Avenue", "New York Avenue",
          "Free Parking", "Kentucky Avenue", "Chance 2", "Indiana Avenue", "Illinois Avenue",
          "B&O Railroad", "Atlantic Avenue", "Ventnor Avenue", "Water Works", "Marvin Gardens",
          "Go To Jail", "Pacific Avenue", "North Carolina Avenue", "Community Chest 3",
          "Pennsylvania Avenue", "Short Line", "Chance 3", "Park Place", "Luxury Tax", "Boardwalk", "In Jail"]
space_to_num = dict(zip(spaces, range(41)))
num_to_space = dict(zip(range(41), spaces))

# Builds lists of all Chance and Community Chest spaces, which are used when handling their behavior
chance_spaces = [space_to_num[f"Chance {i}"] for i in range(1, 4)]
community_chest_spaces = [space_to_num[f"Community Chest {i}"] for i in range(1,4)]

# Builds a dictionary to keep track of how many times each space has been landed on
counter = dict(zip(spaces, [0 for i in range(len(spaces))]))
num_doubles = 0
jail_rolls = 0

# Runs the simulation
current_space = space_to_num["Go"]
for i in range(num_turns):
    take_turn()
    counter[num_to_space[current_space]] += 1

print_results()
