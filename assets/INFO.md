# STORY
 - Build up your stats to defeat the "unbeatable" demon at the end of the level
 - All boss fights are there to test you if you can even defeat it
    - After you beat them in the test, they sacrifice themselves and pass their abilities to you


# CHARACTER
## CHUNAMI
### Description
 - Has an army of drones that will shoot down on the player

### Attacks
1. Shoots bullets in the player's direction
2. Shoots bullets in a pattern, not specific to the player's direction
3. Summons a couple of drones that shoots bullets in a specific pattern
4. Summons a drone that shoots a large laser beam towards the player in a specific pattern
5. Throws bombs that goes towards the player's side as a quadratic slope

### Defensives
1. Summons drones that circle around her acting like a living barrier

### Artificial Intelligence
Every tick, there is a slight chance an attack will occur.
```
current_attacks = {1, 2, 3}
current_defenses = {}
if current_health <= (2/3) * max_health:
    unlock_attack(4)
    unlock_attack(5)
if current_health <= (1/3) * max_health:
    unlock_attack(6)
    unlock_defensive(1)
```