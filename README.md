# Report.

## Requirements

```
Python v-3.7+
music21 v-7.3.
mido v-1.2.
```
## Algorithm.

```
The algorithm is a basic genetic algorithm, wheregenomes are combinations of chords
one for every quarter beat and populations are collections of genomes.
```
## Representation.

```
Genomes are matrices of Nx3, meaning there’re N chordsin each and every chord is a
triad. N gets parsed as a total quantity of quarter beats from track, which is simply
ticks/ticks_per_beat. Each chord consists of notes each of which is an integer denoting certain
note in midi. Populations being lists of genomes are tenzors of MxNx3, where M is a population
limit set manually. There’s also a list of lists of integers which denotes notes that sound, even
though only partially, in certain quarters. Finally there’s a list of chords, meaning matrix 7x3, of
available chords each for each step for the tonality corresponding the given track.
```
## Variation Operators:


 #### Mutation.

    
    Mutation takes a genome, tonic, so called mode_intand num with probability, the
    last two are optional and preset, though could be changed when calling the function.
    Tonic here and after is the tonic of the input track.mode_int equals 1 if track’s mode is
    minor and 0 if it’s major. Num and probability are, self explanatory, number and
    probability of mutation for one call.
    Mutation picks a random index and with given probability tries, and does if
    possible, change a chord by the index in genome to sus2 or sus4, then it swaps to
    arbitrary chords in the genome with chance of 2; and it does all above num times.
    
 #### Crossover.

    
    Takes and returns 5 genomes. When it takes them it  arranges them and shifts their
    slices from arbitrary index by one, changing each of them. Then it returns those changed
    genomes.
     

## Fitness Function.


```
Takes a genome and a list of lists of notes for each quarter beat. Starts with fit = 0. For
each quarter beat it checks corresponding chord and each note in it to be present in the list. If it
is, increments fit by 200. If the chord is sus, add 25 more.
```
## Selection.

```
Returns N first genomes from provided populationthat was sorted by genomes’ fitness in
descending order. N is preset to 5, which is required by crossover.
```
## Main method.

```
Parse all the data needed from the track, tonic,mode, cords pool, etc., generate
population. For population_limit times do the following: sort population, check whether the first
genome satisfies fitness_limit, if it doesn’t slice of last 5 genomes, using selection function pick
5 parents, perform crossover, mutation over the offsprings and add them to the sliced population.
Finally save the first genome of the sorted population using mido as second track to the initial
file.
```
## Preset of Parameters.

```
Although main parameters can be easily changed manually,I chose following values to
be universally optimal for any track within reason:
population_limit = 100
generation_limit = 200
fitness_limit = 200 * len(notes_arr) * 0.95 as something barely reachable with
given fit increase for provided fit increase
probability = 0.001, otherwise there will be too many sus2 and sus4 chords
Everything else varies from implementation to another, which makes no sense to
describe it in details.
```

