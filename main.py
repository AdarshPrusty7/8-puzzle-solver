import copy
import queue  # Needed for priority queue
import time  # Used to keep track of how long algorithm takes


class State:
    # By 'State' I mean each arrangement of the tiles. State is just more readable.

    def __init__(self, parent=None, arrangement=None):
        """
        This is the constructor method
        :param parent: The previous node on the A* tree
        :param arrangement: The specific tile arrangement of this node
        """
        self.parent = parent
        self.arrangement = arrangement
        self.neighbours = []  # Surrounding nodes

        # Now we initialise the values needed for A*
        self.f = 0
        self.g = 0
        self.h = 0

    # Wrote this because I kept getting an error when evaluating fvals
    def __lt__(self, other):
        return self.f < other

    def __gt__(self, other):
        return self.f > other


def neighbourGeneration(state: State):
    """
    Generates neighbour states based on moving the 0/blank tile up, down, left or right
    :return: A list of states
    """

    # Finds the coordinates of the blank tile on the given state
    blankCoords = indexFinder(state, 0)  # 0 is the equivalent of our blank tile in this
    xCoord = blankCoords[0]
    yCoord = blankCoords[1]

    # Finds all potential neighbours and checks if they're within grid constraints
    potentialNeighbours = [[xCoord, yCoord + 1], [xCoord, yCoord - 1], [xCoord + 1, yCoord], [xCoord - 1, yCoord]]
    neighbourCoords = []
    neighbours = []
    arrayLength = len(state.arrangement[0])
    for neighbour in potentialNeighbours:
        if 0 <= neighbour[0] < arrayLength and 0 <= neighbour[1] < arrayLength:
            neighbourCoords.append(neighbour)

    # Creates new States based on previous coordinates + checks to see if they're repeats of their 'grandparent' States
    # We aim for A -> B -> C format. A -> B -> C can lead to infinite loops so we weed it out
    for coords in neighbourCoords:
        neighbour = neighbourMaker(state, coords, blankCoords)
        if state.parent != None:
            if state.parent.arrangement != neighbour.arrangement:
                neighbours.append(neighbour)
        else:
            neighbours.append(neighbour)

    # Final assignment
    state.neighbours = neighbours


def neighbourMaker(parentState: State, moveCoords: list, blankCoords: tuple) -> State:
    """
    Creates neighbour state using coords given
    :param parentState: The parent State of the State that is to be generated
    :param moveCoords: The coordinates that make new State different from parent
    :param blankCoords: The coordinates of the blank tile
    :return: A neighbour State
    """
    # I create a new list entirely to avoid variable referencing the same object in memory accidentally
    newState = State(parentState, [x[:] for x in parentState.arrangement])
    newState.g += 1

    # Basic 3-point swap
    tempSwapNumber = newState.arrangement[moveCoords[0]][moveCoords[1]]
    newState.arrangement[moveCoords[0]][moveCoords[1]] = 0
    newState.arrangement[blankCoords[0]][blankCoords[1]] = tempSwapNumber
    return newState


def aStar(algoType: str, start: list, goal: list):
    """
    This function is the main A* function
    :param algoType: The type of algorithm being used (Hamming or Manhattan)
    :param start: The initial arrangement of tiles
    :param goal: The goal arrangement of tiles
    :return: N/A
    """
    # Assigns the given algorithm type as a variable
    algo = manhattan
    if algoType.lower() == "h":
        algo = hamming

    # Sets up basic
    startTime = time.time()
    openpqueue = queue.PriorityQueue()

    # Creates empty States
    startState = State(None, start)
    goalState = State(None, goal)

    # Sets up the starting State and puts it in the open queue
    startState.g = 0
    startState.h = algo(startState, goalState)
    startState.f = startState.g + startState.h
    openpqueue.put(startState, 9999 - startState.f)  # I have done 9999-X so the highest priority in queue has lowest f

    finalState = None  # So we can reference the final path
    while openpqueue.qsize() != 0:  # According to docs, .empty() is 'unreliable'
        currentState = openpqueue.get()  # Gets the State with lowest f/ highest priority

        # If goal is found, assigns finalState
        if currentState.arrangement == goal:
            finalState = currentState
            break

        # Generates neighbours
        neighbourGeneration(currentState)

        #  Puts all neighbours in open list
        #  States with same arrangement are considered different because different paths are taken
        for neighbour in currentState.neighbours:
            neighbour.g = currentState.g + 1
            neighbour.h = algo(neighbour, goalState)
            neighbour.f = neighbour.g + neighbour.h
            openpqueue.put(neighbour, 9999 - neighbour.f)

    # STOP THE TIMER!!
    end = time.time()

    #  deep copied because States have multiple attributes. If not, could lead to same object reference
    currentState = copy.deepcopy(finalState)
    counter = 0  # Counts how many moves were made
    while True:  # Prints each arrangement by backtracking through parents
        print(('\n'.join(' '.join(str(x) for x in row) for row in currentState.arrangement)), counter)
        if currentState.parent is None:
            break
        currentState = currentState.parent
        counter += 1

    print("steps: " + str(finalState.g))
    print("time: " + str(end - startTime))


def manhattan(state: State, goal: State) -> int:
    """
    This function calculates the Manhattan distance of a given tile arrangement
    :param state: The arrangement of tiles given, whose Manhattan distance must be calculated (2D array)
    :param goal: The goal arrangement of tiles
    :return: An integer, the Manhattan distance
    """
    arrangement = state.arrangement
    totalManhattan = 0
    for initRow in enumerate(arrangement):  # gets the row of the arrangement
        for i in enumerate(initRow[1]):  # get the column of the arrangement
            startCoords = (initRow[0], i[0])  # (x, y) format
            endCoords = indexFinder(goal, arrangement[initRow[0]][i[0]])  # Finds the same coord in the other State
            # Calculates Manhattan distance
            manhattanDistance = abs(startCoords[0] - endCoords[0]) + abs(startCoords[1] - endCoords[1])
            totalManhattan += manhattanDistance
    return totalManhattan


def hamming(state: State, goal: State) -> int:
    """
    This function calculates the Hamming distance of a given tile arrangement
    :param state: The arrangement of tiles given, whose Hamming distance must be calculated (2D array)
    :param goal: The goal arrangement of tiles
    :return: An integer, the Hamming distance
    """
    arrangement = state.arrangement
    goalArrangement = goal.arrangement
    totalHamming = 0
    for row in enumerate(arrangement):
        for item in enumerate(row[1]):
            # Simply counts the number of differences between state and goal
            if arrangement[row[0]][item[0]] != goalArrangement[row[0]][item[0]]:
                totalHamming += 1
    return totalHamming


def indexFinder(state: State, tile: int) -> tuple:
    """
    This function finds where in an arrangement the given tile is
    :param state: The arrangement of tiles given
    :param tile: The tile/ number that must be found
    :return: Tuple coordinates of where in the arrangement the tile is
    """
    for col, row in enumerate(state.arrangement):
        if tile in row:
            return col, row.index(tile)


def main():
    """
    This is the main function of the program.
    The user may set their initial and final states and the solution,
    steps and time taken to calculate it will be printed
    """
    # User input
    start = ""
    end = ""
    size = ""

    # Populates the lists initially just in case
    startList = []
    endList = []


    while not size.isdigit():
        size = input("Please enter the size of your square grid as an integer e.g. 5")

    size = int(size)
    # Basic validation to check whether size^2 digits long + all digits
    while len(start) != size**2 or not start.isdigit():
        start = input("Please enter a starting state e.g. 123456780\n")
    while len(end) != size**2 or not end.isdigit():
        end = input("Please enter a goal state e.g. 123456780\n")

    # Turns the given string into a list for easy iteration
    start = list(map(int, start))
    end = list(map(int, end))

    # Converts string to 2d array
    counter = 0
    for i in range(0, size):
        startList.append([])
        endList.append([])
        for x in range(0, size):
            startList[i].append(int(start[counter]))
            endList[i].append(int(end[counter]))
            counter += 1

    # Basic validation to check whether they want Manhattan or Hamming distance calculated.
    algoType = ""
    while (algoType.lower() != 'm') and (algoType.lower() != 'h'):
        algoType = input("Please type your preferred algorithm. Manhattan (press 'm') or Hamming (press 'h') ")
        pass

    aStar(algoType, startList, endList)


main()
