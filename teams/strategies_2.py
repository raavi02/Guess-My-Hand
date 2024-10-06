import random
from CardGame import Deck

PARTNERS = {
    'North': 'South',
    'East': 'West',
    'South': 'North',
    'West': 'East',
}

deck = Deck()
previous_guesses = []  # Global variable to keep track of previous guesses

RANKED_CARD_VALUES = deck.values


def playing(player, deck):
    """
    Playing strategy goes here (what card will the player expose to their partner)
    """
    if not player.hand:
        return None

    # Todo set lower bound (maybe on suit?) to get a smaller range for guessing.
    card_to_play = get_max_value_index(player)
    print("Play: ", card_to_play)
    return card_to_play


def get_max_value_index(player):
    """
    Play card to create upper bound value.
    """
    max_index = 0
    max_value = -1

    for i, card in enumerate(player.hand):
        value = RANKED_CARD_VALUES.index(card.value)
        if value > max_value:
            max_value = value
            max_index = i
    return max_index


def use_max_value_index(exposed_card, guess_deck, round):
    """
    Use the upper bound value strategy to inform guess
    """
    print(f"Exposed Card: {exposed_card}")
    # Get ranked value index of the card your partner exposed
    for index, value in enumerate(RANKED_CARD_VALUES):
        if value == exposed_card.value:
            print(f"Value exposed as upper bound: {value} with the index of {index}")
            max_value_index = index
            break

    possible_values = RANKED_CARD_VALUES[:max_value_index + 1]
    print(f"Remaining possible values: {possible_values}")
    for card in guess_deck:
        if card.value not in possible_values:
            guess_deck.remove(card)
            print(f"Removed {card}")

    # Todo this would be improved by guessing all suits of that max value of the card that our partner exposed (since it is asserting that they have at least one card to set that max).

    return random.sample(guess_deck, 13 - round)


def get_guess_deck(player, cards):
    """
    This function takes in the list of all cards in the game and removes cards that would be illogical guesses.
    Illogical guesses include:
        - Cards in the players own hand
        - Cards that have been exposed by other players in the game

    :param player:
    :param cards: list[Card]
    :return: list[Card]
    """
    # Remove cards in player's hand
    guess_deck = set(cards) - set(player.hand)
    # Remove cards that have been exposed
    for _, exposed_cards in player.exposed_cards.items():
        if len(exposed_cards) > 0:
            guess_deck = guess_deck - set(exposed_cards)
    return list(guess_deck)


def get_partner_exposed_card(player):
    return player.exposed_cards[PARTNERS[player.name]][-1]


def guessing(player, cards, round):
    """
    Guessing strategy goes here (number of guesses of your partner's cards)
    """
    print(" ")
    print(f"Player: {player.name}")
    global previous_guesses

    ############### Tom (10/3):
    if round == 1:  # The initial round
        create_card_dictionary(cards)  # Initialize the dictionary
        previous_guesses = []  # Initialize previous guesses to an empty list

        # Simulate that after 4 cards are exposed, you update the probabilities
        # (since your partner does not have any of the exposed cards)
        total_possible_cards = 52 - 16  # 52 - (your hand + exposed cards)
        partner_hand_size = 12  # Partner has 12 unexposed cards

        # Assign initial uniform probability to remaining 36 cards
        for idx, value in guesser_card_dict.items():
            value[1] = 1  # Numerator
            value[2] = 36  # Denominator (since 36 cards are possible)

        print("Initial Probabilities After 4 Cards Exposed:")
        for idx, value in sorted(guesser_card_dict.items()):
            card = value[0]
            prob = value[1] / value[2]
            print(f"{card}: {prob:.4f}")
    else:
        # After receiving the c_value from the previous round
        if player.cVals:
            c_value = player.cVals[-1]  # Get the last c_value
            # Update the list of total possible cards (K)
            total_possible_cards = len(guesser_card_dict)
            # Calculate the partner's current unexposed hand size (M)
            partner_hand_size = 13 - (round - 1)  # Since partner exposes one card each round
            update_probabilities(previous_guesses, c_value, total_possible_cards, partner_hand_size)
            # Print updated probabilities
            print("Updated Probabilities:")
            # Sort probabilities in descending order
            sorted_probs = sorted(
                ((value[0], value[1] / value[2]) for value in guesser_card_dict.values()),
                key=lambda x: -x[1]
            )
            for card, prob in sorted_probs:
                print(f"{card}: {prob:.4f}")

    guess_deck = get_guess_deck(player, cards)
    exposed_card = get_partner_exposed_card(player)

    # Partner player's exposed card is used as an upper bound for values to guess from.
    guesses = use_max_value_index(exposed_card, guess_deck, round)

    previous_guesses = guesses

    print(player.cVals, sum(player.cVals))
    return guesses


################################################################################################################### Tom (10/3):
guesser_card_dict = {}


def hash_card_index(card):
    """
    This function maps cards to an index and scrambles the index.
    """
    suit_order = {"Hearts": 0, "Diamonds": 2, "Clubs": 1, "Spades": 3}
    value_order = {"2": 7, "3": 10, "4": 4, "5": 5, "6": 11, "7": 3, "8": 2, "9": 13, "10": 6, "J": 1, "Q": 9, "K": 12,
                   "A": 8}

    # Hash formula that combines suit and value in a less predictable way
    suit = suit_order[card.suit]
    value = value_order[card.value]

    index = suit * 13 + value

    return index


def create_card_dictionary(deck):
    """
    This function takes in a deck of cards and fills in a dictionary where:
    - Key: The scrambled index from hash_card_index
    - Value: A list:
    [card in Card, numerator in int, denominator in int, is_certain in boolean, is_in_partner_hand in bool2]
    """
    counter = 0
    for card in deck:
        index = hash_card_index(card)
        guesser_card_dict[index] = [card, 1, 52, False, False]  # Initializing with 2 integers and 2 booleans
        counter += 1
    return 1


##############################################################################################################

def update_probabilities(guesses, c_value, total_possible_cards, partner_hand_size):
    N = len(guesses)  # Number of guesses made in the previous round
    K = total_possible_cards  # Total possible cards that could be in partner's hand
    M = partner_hand_size  # Partner's current unexposed hand size after exposing a card
    C = c_value  # Number of correct guesses

    if N == 0 or K - N == 0:
        print("Division by zero encountered in update_probabilities.")
        return

    guessed_card_factor = C / N
    unguessed_card_factor = (M - C) / (K - N)

    total_probability = 0  # To accumulate total probability for normalization

    for index, value in guesser_card_dict.items():
        card = value[0]
        old_prob = value[1] / value[2] if value[2] != 0 else 0

        if card in guesses:
            new_prob = old_prob * guessed_card_factor
        else:
            new_prob = old_prob * unguessed_card_factor

        value[1] = new_prob
        value[2] = 1

        total_probability += new_prob

    # Normalize probabilities so that they sum to M (current partner hand size)
    if total_probability == 0:
        print("Total probability is zero after updates. Cannot normalize probabilities.")
        return

    normalization_factor = M / total_probability

    for index, value in guesser_card_dict.items():
        prob = value[1] / value[2]
        normalized_prob = prob * normalization_factor
        value[1] = normalized_prob  # Update numerator with normalized probability
        value[2] = 1  # Denominator remains 1