"""
A text-based implementation of Hearts, a classic trick-taking game played with a standard deck of playing cards

Games are played against three computer opponents.  The AI of the opponents is primitive - they will never cheat, but
they will not play with any strategy.
"""

import random
from time import sleep


# A generic player class, which is inherited by both the Human and Computer classes
class Player:
    def __init__(self):
        self.hand = []
        self.penalty_cards = []
        self.score = 0
        self.incoming_cards = []

    # Determines if the player has the lead suit
    def has_lead_suit(self, lead_suit):
        for card in self.hand:
            if card[1] == lead_suit:
                return True
        return False

    def organize_hand(self):
        organized_hand = []
        for suit in ["C", "S", "H", "D"]:
            for rank in range(2, 15):
                if (rank, suit) in self.hand:
                    organized_hand.append((rank, suit))
        self.hand = organized_hand


# Used to create the Human player object
class Human(Player):
    def __init__(self):
        super().__init__()
        self.name = "You"

    def print_hand(self):
        for card_num, card in enumerate(self.hand):
            print("{:<2} {:>3}".format(card_num + 1, get_card_name(card)))

    # Determines which card the player will play on their turn
    def play_card(self, lead_suit, leading, first_trick, hearts_broken):
        # If the player has the 2 of Clubs, they must play it
        if (2, "C") in self.hand and first_trick:
            self.hand.remove((2, "C"))
            return 2, "C"
        else:
            while True:
                print()
                if leading:
                    if hearts_broken:
                        print("Hearts have been broken.")
                    else:
                        print("Hearts have not been broken.")
                else:
                    print("Lead suit: " + lead_suit)
                print("Choose a card to play.")
                print()
                self.print_hand()
                print()
                user_input = input()

                # Gets input from the user on which card to play
                try:
                    card_to_play = self.hand[int(user_input) - 1]
                except (ValueError, IndexError):
                    print("Please enter a valid number.")
                    sleep(3)
                    continue

                # Handles playing a card when leading the trick
                if leading:
                    if hearts_broken or card_to_play[1] != "H":
                        self.hand.remove(card_to_play)
                        return(card_to_play)
                    else:
                        print("Hearts are not broken.  Play a different card.")

                # Handles playing a card when not leading the trick
                else:
                    # Makes sure you follow suit if possible
                    if card_to_play[1] == lead_suit or not self.has_lead_suit(lead_suit):
                        # Makes sure you don't play points on the first trick
                        if not first_trick or (card_to_play[1] != "H" and card_to_play != (12, "S")):
                            self.hand.remove(card_to_play)
                            return(card_to_play)
                        else:
                            print("You cannot play penalty cards on the first trick.")
                    else:
                        print("You must follow suit.")
                print()
                print()
                sleep(3)

    def pass_cards(self, pass_direction, pass_name):
        while True:
            print("You are passing {} to {}.".format(pass_direction, pass_name))
            print("Choose three cards to pass.")
            print()
            self.print_hand()
            print()
            user_input = input()
            try:
                input_list = list(map(lambda x: int(x), user_input.split()))
                input_list = set(input_list)
                if len(input_list) != 3:
                    raise IndexError
                cards_to_pass = [self.hand[x-1] for x in input_list]
            except (ValueError, IndexError):
                print("Please enter three valid numbers")
                sleep(3)
                continue
            break

        for card in cards_to_pass:
            self.hand.remove(card)
        return cards_to_pass


# Used to create the three computer player objects
class Computer(Player):
    def __init__(self):
        super().__init__()
        self.name = random.choice(names)
        names.remove(self.name)

    # Determines which card the computer will play
    # This is done by determining which cards are legal to play and randomly choosing one
    def play_card(self, lead_suit: str, leading: bool, first_trick, hearts_broken: bool):
        if (2, "C") in self.hand:
            card_to_play = (2, "C")
        else:
            if leading:
                if hearts_broken:
                    card_to_play = random.choice(self.hand)
                else:
                    viable_cards = list(filter(lambda card: card[1] != "H", self.hand))
                    if len(viable_cards) > 0:
                        card_to_play = random.choice(viable_cards)
                    else:
                        card_to_play = random.choice(self.hand)
            else:
                if self.has_lead_suit(lead_suit):
                    viable_cards = list(filter(lambda card: card[1] == lead_suit, self.hand))
                    card_to_play = random.choice(viable_cards)
                else:
                    card_to_play = random.choice(self.hand)

        self.hand.remove(card_to_play)
        return card_to_play

    # Used to determine which 3 cards to pass at the start of each hand, which is done at random
    def pass_cards(self, *args):
        cards_to_pass = []
        for num in range(3):
            card = random.choice(self.hand)
            cards_to_pass.append(card)
            self.hand.remove(card)
        return cards_to_pass


def play_game():
    def play_hand(hand_num):
        def deal_cards():
            # Builds deck
            deck = []
            for suit in ["H", "D", "S", "C"]:
                for rank in range(2, 15):
                    deck.append((rank, suit))
            random.shuffle(deck)
            # Deals cards
            for player in players:
                player.hand.extend([deck.pop() for x in range(13)])
                player.organize_hand()

        def pass_cards():
            for player_pos, player in enumerate(players):  # For each player:
                player_to_pass_to = (player_pos + player_pass_num) % 4  # figures out which player they will pass to
                pass_direction = {1: "left", 2: "across", 3: "right"}[
                    player_pass_num]  # gets the name of the direction being passed to display to the screen
                pass_name = players[player_to_pass_to].name  # gets the name of the player being passed to
                cards_to_pass = player.pass_cards(pass_direction,
                                                  pass_name)  # gets the cards the passing player wants to pass
                players[player_to_pass_to].incoming_cards = cards_to_pass  # passes the cards
            for player in players:
                player.hand.extend(player.incoming_cards)  # adds cards passed to each player to that player's hand
                player.organize_hand()

        def play_trick(leading_player, first_trick, hearts_broken):

            # Everyone plays a card
            played_cards = [None, None, None, None]
            for num in list(range(4)):
                current_player = (num + leading_player) % 4
                if current_player == leading_player:
                    played_cards[current_player] = players[current_player].play_card("any", True, first_trick,
                                                                                     hearts_broken)
                    lead_suit = played_cards[current_player][1]
                else:
                    played_cards[current_player] = players[current_player].play_card(lead_suit, False, first_trick,
                                                                                     hearts_broken)
                print(players[current_player].name + " played " + get_card_name(played_cards[current_player]))
                sleep(2)

            # Checks if hearts were just broken
            for card in played_cards:
                if card[1] == "H":
                    hearts_broken = True

            # Determines winner of trick
            highest_card = (0, 0)
            for pos, card in enumerate(played_cards):
                if card[1] == lead_suit and card[0] > highest_card[0]:
                    highest_card = card
                    highest_pos = pos
            print(players[highest_pos].name + " won the trick.")
            sleep(3)
            print()
            print()
            print()

            # Gives penalty cards to winner of trick
            for card in played_cards:
                if card == (12, "S") or card[1] == "H":
                    players[highest_pos].penalty_cards.append(card)

            # Returns winning player to lead the next trick
            return highest_pos, hearts_broken

        def print_scores():
            width = 16
            print("|" + "SCORES".center(width - 2, "=") + "|")
            for player in players:
                score = "|" + player.name.ljust(width - 5, ".") + str(player.score).rjust(3, "0") + "|"
                print(score)
            print("|" + "=" * (width - 2) + "|")
            print()
            print()

        hearts_broken = False
        deal_cards()
        pass_cards()

        # Finds the player holding the 2 of Clubs and sets them to lead the first trick
        for player_pos, player in enumerate(players):
            if (2, "C") in player.hand:
                leading_player = player_pos
                break

        # Plays the hand
        print("Hand " + str(hand_num))
        sleep(3)
        first_trick = True
        for i in range(13):
            leading_player, hearts_broken = play_trick(leading_player, first_trick, hearts_broken)
            first_trick = False

        # Checks if someone shot the moon
        shot_moon = None
        for player in players:
            if len(player.penalty_cards) == 14:
                shot_moon = player.name
                print(f"{player.name} shot the moon!")

        # Distributes points
        for player in players:
            if shot_moon:
                if player.name != shot_moon:
                    player.score += 26
            else:
                for card in player.penalty_cards:
                    if card == (12, "S"):
                        player.score += 13
                    else:
                        player.score += 1

        # Displays scores
        print_scores()

    player1 = Human()
    player2 = Computer()
    player3 = Computer()
    player4 = Computer()
    players = [player1, player2, player3, player4]

    player_pass_num = 0
    hand_num = 1
    game_running = True
    while game_running:
        player_pass_num = [0, 1, 3, 2][hand_num % 4]  # finds the next direction to pass cards
        play_hand(hand_num)
        hand_num += 1
        for player in players:
            if player.score >= 100:
                game_running = False

    lowest_score = 1000
    for player in players:
        if player.score < lowest_score:
            winner = player
            lowest_score = player.score

    print(f"Winner: {winner.name} with {winner.score} points!")


def get_card_name(card):
    rank_names = {11: "J", 12: "Q", 13: "K", 14: "A"}
    if card[0] < 11:
        return str(card[0]) + card[1]
    else:
        return rank_names[card[0]] + card[1]


# Pool of names that is used to randomly name the computer opponents
names = """Alice Andy Bob Cindy Clark Dan Danielle Ellen Frank Fiona Gina Gavin Henry Heather Isabel John Jasmine 
Kayla Kyle Leon Mary Max Nick Nancy Paige Paul Rick Sam Sally Tammy Victor Wendy Xavier Yvette""".split()

play_game()
