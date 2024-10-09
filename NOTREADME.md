//future ups"
Run path finding algorithm and cut down the path to a one dimensional chunk.

Run through step 1 again and again till that particular chunk is exhausted.

run through distance check and visibilty check and if okay then run first step again else just stand or idle around. For more complex ai you could add an intermediate mode that for a certain time it calculates and follows the path where the player could have gone after he went out of sight and if player is still not visible, then enter idle mode (walk around, observe surroundings)

repeat above steps till zombie reaches a distance where it can attack the player and enter attacking mode. You have the choice to make the zombie stationary or let it run pathfinding and follow player in between and during attacks.
