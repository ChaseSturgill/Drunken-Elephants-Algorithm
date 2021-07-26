#python libraries
from random import Random   #need this for the random number generation
import numpy as np
from itertools import chain


#to setup a random number generator, we will specify a "seed" value
#need this for the random number generation
seed = 51132021
myPRNG = Random(seed)

#to get a random number between 0 and 1, use this:             myPRNG.random()
#to get a random number between lwrBnd and upprBnd, use this:  myPRNG.uniform(lwrBnd,upprBnd)
#to get a random integer between lwrBnd and upprBnd, use this: myPRNG.randint(lwrBnd,upprBnd)

#number of elements in a solution
n = 150

#create an "instance" for the knapsack problem
value = []
for i in range(0,n):
    value.append(round(myPRNG.triangular(150,2000,500),1)) #Low, High, Mode for traingular
    
weights = []
for i in range(0,n):
    weights.append(round(myPRNG.triangular(8,300,95),1)) #Low, High, Mode for traingular
    
#define max weight for the knapsack
maxWeight = 1500

#monitor the number of solutions evaluated
solutionsChecked = 0

#function to evaluate a solution x
def evaluate(x):
          
    a=np.array(x)
    b=np.array(value)
    c=np.array(weights)
    
    totalValue = np.dot(a,b)     #compute the value of the knapsack selection
    totalWeight = np.dot(a,c)    #compute the weight value of the knapsack selection

    if totalWeight > maxWeight:
        totalValue = 0  #set value to 0 to ensure solution is not selected, technically could be 149.999 since our lowest allowed value is 150
    
    return [totalValue, totalWeight]   #returns a list of both total value and total weight
          
       
#here is a simple function to create a neighborhood
#1-flip neighborhood of solution x         
def neighborhood(x):
        
    nbrhood = []     #empty list 
    
    for i in range(0,n):
        nbrhood.append(x[:])    #appending original solution, setting up 150 neighbors
        if nbrhood[i][i] == 1:  #if ith element of list i is 1, flip to 0 (moving to a neighbor)
            nbrhood[i][i] = 0
        else:
            nbrhood[i][i] = 1   #if ith element of list i is 0, flip to 0 (moving to a neighbor)
      
    return nbrhood
          


#create the initial solution
def initial_solution():
    x = [0] * n   #list of 150 zeros to initiate x

    c=np.array(weights) #local array of weight, c is used to match neighborhood function
    totalWeight = 0 #initiate total weight to be 0

    while totalWeight <= maxWeight:
        ranIndex = myPRNG.randint(0, n) #generate a random index
        a=np.array(x)   #turn list into array
        if np.dot(a,c) + c[ranIndex] >= maxWeight:    #check if the new weight is greater than the max weight
            break   #break the while loop, new item would put the knapsack over the weight limit
        else:
            x[ranIndex] = 1 #include the item in the knapsack
            totalWeight = np.dot(a,c)   #generate the new max weight

    return x

#varaible to record the number of solutions evaluated
solutionsChecked = 0

p = 0.9 #probability threshold
k = 3  #searches to run in parallel
tabu = [] #initalize tabu memory, this will track the indices of additional items added to the knapsack
for i in range (0, k):
    tabu.append([])

#initialize list of initial solutions based on number of restarts, chosing to start with best and create curr later
x_best = []    
for i in range(0, k):
    x_best.append(initial_solution())  


f_best = []
for i in range(0, k):
    f_best.append(evaluate(x_best[i]))  

#begin local search overall logic ----------------
done = 0
iterations = 0
    
while done == 0:
    
    #Reset tenure is 3 iterations
    if iterations % 3 == 0:
        tabu = []
        for i in range (0, k):
            tabu.append([])

    Neighborhood = [] #Initiliaze neighborhood
    local_values = [] #list to hold values for every neighborhood

    #create a list of all neighbors in the neighborhoods of x_best and generate empty tabu_Neighborhood
    tabu_Neighborhood = []
    for i in range(0, k):
        Neighborhood.append(neighborhood(x_best[i]))  
        tabu_Neighborhood.append([])

    #Generate tabu neighborhoods
    for h in range(0, k):
        if (len(tabu[h]) > 0):
            for i in range(0, n):
                matches = 0
                for j in range(0, len(tabu[h])):
                    if Neighborhood[h][i][tabu[h][j]] == 1:
                        matches += 1

                if matches == len(tabu[h]) or evaluate(Neighborhood[h][i])[0] > f_best[h][0]:
                    tabu_Neighborhood[h].append(Neighborhood[h][i])
        else: 
            tabu_Neighborhood[h] = Neighborhood[h]
        
    flat_Neighborhood = list(chain.from_iterable(tabu_Neighborhood)) #unnest nested list of Neighborhood
    
    randNum = myPRNG.random()          #generate random probability
    if randNum < (1 - p):
        #list of feasible neighborhoods to use for random walk
        feasible_Neighborhood = []
        for i in range(0, len(flat_Neighborhood)):
            if (evaluate(flat_Neighborhood[i])[0] > 0):
                feasible_Neighborhood.append(flat_Neighborhood[i])

        #pick k random neighbors and update current values
        x_curr = []
        for i in range(0, k):
            x_curr.append(myPRNG.choice(feasible_Neighborhood))

        f_curr = []
        for i in range(0, k):
            f_curr.append(evaluate(x_curr[i]))
            solutionsChecked += 1 

        #Track index of items that were added to the knapsack
        for i in range(0, k):
            for j in range(0, n):
                if (x_curr[i][j] - x_best[i][j]) == 1:
                    tabu[i].append(j)

        #update best and keep random solutions
        x_best = x_curr[:]
        f_best = f_curr[:]


    else: 
        #create list with the values from all neighborhoods to find highest values
        for i in range (0, len(flat_Neighborhood)):
            local_values.append(evaluate(flat_Neighborhood[i])[0])
            solutionsChecked += 1 #updating solutions checked here since all neighborhoods are evaluated

        #find the indices from local_values of the highest k values
        f_curr_indices = []
        f_curr_indices = sorted(range(len(local_values)), key=lambda i: local_values[i], reverse=True)[:k]

        #list for k new possible solutions based on highest values
        x_curr = []
        for i in f_curr_indices:
            x_curr.append(flat_Neighborhood[i])

        #list for the values and weights of k possible solutions with the highest values
        f_curr = []
        for i in f_curr_indices:
            f_curr.append(evaluate(flat_Neighborhood[i]))

        #if no neighborhood is greater than one of the starting parallel solutions, then end the loop
        if (max(f_curr, key=lambda x: x[0])[0] <= max(f_best, key=lambda x: x[0])[0]):
            done = 1

        #if a new max is found, then move to the highest k solutions
        else:

            #Track index of items that were added to the knapsack
            for i in range(0, k):
                for j in range(0, n):
                    if (x_curr[i][j] - x_best[i][j]) == 1:
                        tabu[i].append(j)

            x_best = x_curr[:]
            f_best = f_curr[:]
    
    iterations += 1
    #print solutions checked and best value so far
    print ("\nTotal number of solutions checked: ", solutionsChecked)
    print ("Best value found so far: ", max(f_best, key=lambda x: x[0])[0])  

print("\nNumber of parallel searches: ", k)
print ("Final number of solutions checked: ", solutionsChecked)
print("Best solution from each parallel seach: ", f_best)
print ("Best value found: ", max(f_best, key=lambda x: x[0])[0])
maxIndex = f_best.index(max(f_best, key=lambda x: x[0])) #gets index of highest value to use to find the solution in the x_best list
print ("Weight is: ", f_best[maxIndex][1])
print ("Total number of items selected: ", np.sum(x_best[maxIndex]))
print ("Best solution: ", x_best[maxIndex])
