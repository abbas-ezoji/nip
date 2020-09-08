import random
from libs.pyeasyga import binary_ga as pyeasyga
# setup seed data
seed_data = [0, 1, 2, 3, 4, 5, 6, 7]
# initialise the GA
ga = pyeasyga.GeneticAlgorithm(seed_data,
                                population_size=200,
                                generations=100,
                                crossover_probability=0.8,
                                mutation_probability=0.2,
                                elitism=True,
                                maximise_fitness=False)
# define and set the GA's selection operation
def selection(population):
    return random.choice(population)

ga.selection_function = selection

# define a fitness function
def fitness (individual, data):
    collisions = 0
    for item in individual:
        item_index = individual.index(item)
        for elem in individual:
            elem_index = individual.index(elem)
            if item_index != elem_index:
                if item - (elem_index - item_index) == elem \
                    or (elem_index - item_index) + item == elem:
                    collisions += 1
    return collisions

ga.fitness_function = fitness # set the GA's fitness function
ga.run() # run the GA

# function to print out chess board with queens placed in position
def print_board(board_representation):
    def print_x_in_row(row_length, x_position):
        print( '',)
        for _ in range(row_length):
            print ('---',)
        print( '\n|',)
        for i in range(row_length):
            if i == x_position:
                print( '{} |'.format('X'),)
            else:
                print (' |',)
        print ('')
    def print_board_bottom(row_length):
        print ('',)
        for _ in range(row_length):
            print ('---',)
            
    num_of_rows = len(board_representation)
    row_length = num_of_rows #rows == columns in a chessboard
    for row in range(num_of_rows):
        print_x_in_row(row_length, board_representation[row])
        
    print_board_bottom(row_length)
    print ('\n')

# print the GA's best solution; a solution is valid only if there are no collisions
if ga.best_individual()[0] == 0:
    print (ga.best_individual())
    print_board(ga.best_individual()[1])
else:
    print( None)