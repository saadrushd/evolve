#!/usr/bin/python3

"""
Created on Thu Jun 28 19:05:38 2018
please see README.org
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import subprocess

# global constants
DNA_LOW = 0   # minimum DNA value
DNA_HIGH = 11 # maximum DNA value
DNA_LEN = 5 # how many cells in each DNA array
ISLANDA_TYPICAL = 8  #the trait islandA demand
ISLANDB_TYPICAL = 2  #the trait islandB demand
INITIAL_POPULATION_NUMBER = 10
NUMBER_OF_GENERATIONS = 15
MAX_POPULATION = 40000 # just to save time cause mating the whole population after 4000 will take ages

# some calculation constants
EXP = 2
FACTOR = 1/8
translate = lambda rank: int((rank**EXP)*FACTOR)

class JesusException(Exception):
    """ raised whenever a child is porn without a father
(this will not be raised actually its just a joke :D)
"""
    pass

def calc_rank(dna, typical):
    rank = sum(abs(dna - typical))/DNA_LEN
    return 8-rank

class Animal():
    def __init__(self, island, mom=None, dad=None):

        if (dad is None) and (mom is None):
            # generation zero
            self.dna = np.random.randint(DNA_LOW, DNA_HIGH, DNA_LEN)
        elif (dad is not None) and (mom is not None):
            midpoint = int(DNA_LEN/2)
            self.dna = np.append(dad.dna[:midpoint], mom.dna[midpoint:])
            random_index = np.random.randint(DNA_LEN)
            self.dna[random_index] = np.random.randint(DNA_LOW, DNA_HIGH)
        else:
            # this will not be raised actually its just a joke :D
            raise(JesusException)

        if island == 'A':
            self.rank = calc_rank(self.dna, ISLANDA_TYPICAL)
        elif island == 'B':
            self.rank = calc_rank(self.dna, ISLANDB_TYPICAL)

        self.island = island
        self.dad = dad
        self.mom = mom
        self.gender = np.random.randint(2) # 0 male 1 female
        self.power = translate(self.rank)
        self.time =  translate(self.rank)

def get_dead_indices(population):
    dead_indices = []
    population_copy_en = enumerate(population[:])
    for i,animal in population_copy_en:
        if animal.time <= 0:
            dead_indices.append(i)
    return dead_indices

def kill_whos_time_has_come(population):
    dead_indices = get_dead_indices(population)
    new_population = []
    for i, animal in enumerate(population):
        if i not in dead_indices:
            new_population.append(animal)
    population = new_population

def haram(female, male):
    return (male == female.dad) or (male.mom == female) \
            or ((male.mom == female.mom) and (male.dad == female.dad) and male.mom is not None)

def create_couples(females, males):
    """
    takes sorted females and males by rank k
    """
    couples  = []
    married_men = set()
    for female in females:
        for male in males:
            if (not haram(female,male))and(male not in married_men) :
                couples.append((female,male))
                married_men.add(male)
                break
    return couples

def decrement_time(population):
    for animal in population:
        animal.time -= 1

def mate(couple):
    mama,papa = couple
    babies_number = min(mama.power, papa.power)
    return [Animal(mama.island, mom=mama, dad=papa) for i in range(babies_number)]

def mating_season(population):
    kill_whos_time_has_come(population)
    decrement_time(population)
    females = [ animal for animal in population if animal.gender]
    males = [ animal for animal in population if not animal.gender]

    females = sorted(females, key = lambda f: f.rank)
    males = sorted(males, key = lambda m: m.rank)

    couples = create_couples(females, males)
    babies = []
    for couple in couples:
        babies += mate(couple)
    population += babies

def get_mean_vals(populationA, populationB):
    dnaA = np.concatenate([animal.dna for animal in populationA])
    dnaB = np.concatenate([animal.dna for animal in populationB])
    return np.mean(dnaA), np.mean(dnaB)

def plot_means(means):
        meansA = [t[0] for t in means]
        meansB = [t[1] for t in means]
        t = list(range(i+2))

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(t, meansA, label='populationA (8)')
        ax.plot(t, meansB, label='populationB (2)')
        ax.legend()
        ax.set_xlabel('time')
        ax.set_ylabel('population DNA average')
        ax.grid()

        figname = f'./output/trial{ntrials}.png'
        fig.savefig(figname)
        subprocess.Popen(['xdg-open', figname])


if __name__ == '__main__':
    ntrials = 0
    while True:
        print(f'-------------trial{ntrials}-------------')

        populationA = [Animal('A') for i in range(INITIAL_POPULATION_NUMBER)]
        populationB = [Animal('B') for i in range(INITIAL_POPULATION_NUMBER)]
        means = [get_mean_vals(populationA, populationB)]

        print('generation zero: ')
        print('the mean of population A dna', means[0][0])
        print('the mean of population B dna', means[0][1])

        iA, iB = 0, 0
        for i in range(NUMBER_OF_GENERATIONS):
            if len(populationA) < MAX_POPULATION:
                mating_season(populationA)
                iA += 1
            if len(populationB) < MAX_POPULATION:
                mating_season(populationB)
                iB += 1
            means.append(get_mean_vals(populationA, populationB))

        ntrials += 1

        print(f'after {min(iA,iB)} generations: ')
        print('the mean of population A dna', means[i][0] )
        print('the mean of population B dna', means[i][1])
        print('with diff ',  means[i][0] - means[i][1])

        plot_means(means)
