import math
from random import choices, randint, randrange, random
from typing import List, Callable, Tuple
import music21
import mido

Chord = List[int]
Genome = List[Chord]

Population = List[Genome]
PopulateFunc = Callable[[], Population]
FitnessFunc = Callable[[Genome], int]
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome], Genome]
PrinterFunc = Callable[[Population, int, FitnessFunc], None]


def generate_genome(chords: List[Chord], length: int = 7) -> Genome:
    return choices(chords, k=length)


def generate_population(chords: List[Chord], size: int, genome_length: int) -> Population:
    return [generate_genome(chords, genome_length) for _ in range(size)]


def crossover(a: Genome, b: Genome, c: Genome, d: Genome, e: Genome) -> [Genome, Genome, Genome, Genome, Genome]:
    """
    Revolves 5 genomes by 1 and swaps their random slices
    :param a: Genome
    :param b: Genome
    :param c: Genome
    :param d: Genome
    :param e: Genome
    :return: list of genomes
    """
    if len(a) * 5 != len(a) + len(b) + len(c) + len(d) + len(e):
        raise ValueError("Genomes a and b must be of same length")

    genomes = [a, b, c, d, e]
    length = len(a)

    p = randint(1, length - 1)
    add = genomes[0][p:]
    for i in range(4):
        genomes[i] = genomes[i][0:p] + genomes[i + 1][p:]
    genomes[4] = genomes[4][0:p] + add
    return genomes


def mutation(tonic: int, mode_int: int, genome: Genome, num: int = 2, probability: float = 0.001) -> Genome:
    """
    According to given probability makes a chord sus if possible and with the chance of 50% swaps two chords
    :param tonic: as midi integer
    :param mode_int: a flag of the mode, is either 0 or 1
    :param genome: to be changed
    :param num: iterations to perform
    :param probability: to make a chord sus. Better make it small
    :return genome: after mutation
    """
    for _ in range(num):
        index1 = randrange(len(genome))
        chord = genome[index1]

        if chord[2] - chord[0] == 7 and chord[1] != chord[0] + 2 and chord[1] != chord[0] + 5 \
                and random() < probability:

            if chord[0] % 12 == tonic + 7 - mode_int:  # 3rd step
                chord[1] = chord[2] - 2
            elif chord[0] % 12 == tonic + 5 + 3 * mode_int:  # 4th step
                chord[1] = chord[0] + 2
            else:
                if random() > 0.5:
                    chord[1] = chord[0] + 2
                else:
                    chord[1] = chord[2] - 2
            genome[index1] = chord
        if random() < 0.5:
            index1 = randrange(len(genome))
            index2 = randrange(len(genome))
            genome[index2], genome[index1] = genome[index1], genome[index2]

    return genome


def fitness_func(genome: Genome, notes_arr: List[List[int]]) -> int:
    """
    Grants additional score for sus chords
    :param genome: to be scored
    :param notes_arr: which is a list of separated notes
    :return: some score for a genome
    """
    fit = 0
    if len(genome) != len(notes_arr):
        raise ValueError("Genomes a and b must be of same length")
    genome_fit = [[genome[i][j] % 12 for j in range(len(genome[i]))] for i in range(len(genome))]  # transposed chords

    for i in range(len(genome)):
        for j in range(3):
            if notes_arr[i].__contains__(genome[i][j]):
                root = genome[i][0]
                if genome_fit[i] == [root, (root + 2) % 12, (root + 7) % 12] \
                        or genome_fit[i] == [root, (root + 5) % 12, (root + 7) % 12]:  # check for sus chords
                    fit += 25
                fit += 200
                break
            elif len(notes_arr[i]) == 0:
                fit += 50
    return fit


def selection_func(population: Population, notes_arr: List[List[int]], n=5) -> Population:
    """
    :param notes_arr:
    :param population:
    :param n: quantity of genomes being selected
    :return: n genomes pick unevenly randomly out of the population
    """
    return choices(
        population=population,
        weights=[fitness_func(gene, notes_arr) for gene in population],
        k=n
    )


def sort_population(population: Population, notes_arr: List[List[int]]) -> Population:
    """
    :return: sorted population according to the fitness function
    """
    return sorted(population, key=lambda x: fitness_func(genome=x, notes_arr=notes_arr), reverse=True)


def chord_pool(mode_mask1: List[int], steps: List[int], mode_mask: List[int], mode_int: int, tonic: int):
    """
    Generates all possible major, minor and diminished chords for all the steps of given tonality
    :param mode_mask1: mask of whether there's a relative shift for minor and major steps
    :param steps: preset step shifts yet to be adjusted
    :param mode_mask: mask of tone shifts for the chords at each step of given tonality
    :param mode_int: a flag of the mode, is either 0 or 1
    :param tonic: as midi integer
    :return pool: List[Chord]
    """
    pool = []
    for i in range(7):
        pool.append(tonic + steps[i] - mode_int * mode_mask1[i])

    pool = [[pool[note], pool[note] + 4 - abs(mode_mask[note] - mode_int), pool[note] + 7] for note in range(7)]
    pool[6 - 5 * mode_int][1] -= mode_int
    pool[6 - 5 * mode_int][2] -= 1
    return pool


def messages_to_notes(messages: list, tpb: int) -> List[List[int]]:
    """
    Parses given track's slice and separates all the notes into quarters where they sound even if partially
    :param messages: track's slice with messages containing notes only
    :param tpb: ticks per beat
    :return notes_arr: which is a list of separated notes
    """

    notes_arr = []
    counter = 0
    size = 0

    for message in messages:
        if message.type == 'note_on' or message.type == 'note_off':
            size += message.time
    size = math.ceil(size / tpb)
    [notes_arr.append([]) for _ in range(size)]
    for message in messages:
        if message.type == 'note_on':
            counter += message.time
        elif message.type == 'note_off':
            for i in range(math.floor(counter / tpb), math.ceil((counter + message.time) / tpb)):
                notes_arr[i].append(message.note)
            counter += message.time
    return notes_arr


def run_genetic_algorithm(population_limit: int = 100, generation_limit: int = 200):
    """
    Sets initial conditions, states and the algorithm's prerequisites, runs it and records output
    :param population_limit: maximal (and only) quantity of genomes in populations
    :param generation_limit: maximal quantity of iterations after which algorithm stops
    """

    filename = 'input3.mid'
    filename_out = 'output1'
    key = music21.converter.parse(filename).analyze('key')
    melody = mido.MidiFile(filename, clip=True)
    notes_arr = messages_to_notes(melody.tracks[1][2:-1], melody.ticks_per_beat)
    mode = key.mode
    mode_int = 0 if mode == "major" else 1 if mode == "minor" else -2 ** 32
    tonic = key.tonic.midi
    volume = 45
    fitness_limit = 200 * len(notes_arr) * 0.95
    mutation_func = mutation
    mode_mask1 = [0, 0, 1, 0, 0, 1, 1]
    steps = [0, 2, 4, 5, 7, 9, 11]
    mode_mask = [0, 1, 1, 0, 0, 1, 1]

    chords = chord_pool(mode_mask1=mode_mask1, steps=steps, mode_mask=mode_mask, mode_int=mode_int, tonic=tonic)
    population = generate_population(size=population_limit, genome_length=len(notes_arr), chords=chords)

    for i in range(generation_limit):
        population = sort_population(population=population, notes_arr=notes_arr)

        if fitness_func(population[0], notes_arr) >= fitness_limit:
            break

        next_generation = population[0:-5]

        parents = selection_func(population, notes_arr)

        offsprings = crossover(parents[0], parents[1], parents[2], parents[3], parents[4])
        offsprings = [mutation_func(genome=offsprings[k], mode_int=mode_int, tonic=tonic) for k in
                      range(len(offsprings))]
        next_generation += offsprings

        population = next_generation

    # transposes accompaniment 1 octave lower than tonic
    best_genome = sort_population(population=population, notes_arr=notes_arr)[0]
    octave = tonic // 12 - 1
    for i in range(len(best_genome)):
        for j in range(len(best_genome[i])):
            best_genome[i][j] = best_genome[i][j] % 12 + octave * 12

    acc_track = mido.MidiTrack()
    for chord in best_genome:
        acc_track.append(mido.Message('note_on', channel=0, note=chord[0], velocity=volume, time=0))
        acc_track.append(mido.Message('note_on', channel=0, note=chord[1], velocity=volume, time=0))
        acc_track.append(mido.Message('note_on', channel=0, note=chord[2], velocity=volume, time=0))
        acc_track.append(mido.Message('note_off', channel=0, note=chord[0],
                                      velocity=volume, time=melody.ticks_per_beat))
        acc_track.append(mido.Message('note_off', channel=0, note=chord[1], velocity=volume, time=0))
        acc_track.append(mido.Message('note_off', channel=0, note=chord[2], velocity=volume, time=0))

    melody.tracks.append(acc_track)
    melody.save(filename_out)
    return


run_genetic_algorithm()
