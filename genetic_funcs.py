import random

# Initial speed @ 1.2s for 100k
# New speed @ 0.6s for 100k
def reproduce(parent1 = '', parent2 = ''):
    # Splitting parent strings at random "and" statements
    parent_1_parts = parent1.split(" and ")
    parent_2_parts = parent2.split(" and ")
    parent_1_parts.extend(parent_2_parts)
    if len(parent_1_parts) != 6:
        return parent1, parent2
    c1 = random.sample(parent_1_parts, 6)

    child1 = c1[0] + " and " + c1[1] + " and " + c1[2]
    child2 = c1[3] + " and " + c1[4] + " and " + c1[5]

    return child1, child2


from timeit import default_timer as timer

def mutate_string(string):
    # Define the sets of characters that can be mutated
    NUMBER_CHARACTERS = '123'
    LETTER_CHARACTERS = 'OHLC'

    # Create lists of positions containing numbers and letters
    number_positions = [i for i, char in enumerate(string) if char.isdigit()]
    letter_positions = [i for i, char in enumerate(string) if char.isalpha() and char != 'a' and char != 'n' and char != 'd']

    if number_positions and letter_positions:
        # Randomly select a position from numbers or letters
        selected_position = random.choice(number_positions + letter_positions)

        # Determine the type of the character at the selected position
        if selected_position in number_positions:
            mutation_characters = NUMBER_CHARACTERS
        else:
            mutation_characters = LETTER_CHARACTERS

        # Generate a random replacement character
        random_character = random.choice(mutation_characters)

        # Replace the character at the selected position with the random character
        string_list = list(string)
        string_list[selected_position] = random_character
        mutated_string = ''.join(string_list)
        
        return mutated_string
    else:
        # If there are no positions to mutate, return the original string
        return string


# start = timer()
# for _ in range(100000):
#     mutate_string('O[-3] > L[-1] and O[-3] > C[-3] and O[-3] > C[-2]')
# end = timer()
# print(f'Time to mutate: {end - start}s')