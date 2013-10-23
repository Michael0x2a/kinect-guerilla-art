# Kinect Guerilla Art

## About 

This was a part of an art exhibit I created for a school project for a philosophy class, where 
people could interact with a fictitious personality named "Charlie" during passing period, 
lunchtime, etc.

## Running the program

To run, simply execute

    python manager.py
    
You must have the following modules installed:

-   pygame
-   PyKinect

## What it does

My art exhibit was designed around several “scenes” or “states”, which I’ve named after various emotions. The exhibit initially starts off in a “Lonely” state. When it detects a human, it switches to a “Hopeful” state where it asks the user if they will play with it or not. If the user choses to play with Charlie, then it asks if the user if it wants to tell jokes or play ping-pong. Asking the user to tell jokes will place Charlie in a “Sad” state, whereas chosing to play ping-pong will put Charlie in a “Happy” state. Charlie never actually starts playing ping-pong: I did not have time to code in a working ping-pong game. It is moot to outline changes in state if the user chose to not play with Charlie, since nobody chose that option.

At any point in time, if the user gets too close to the Kinect, it enters into a “Scared” state and asks the user to step back. If the user fails to make a choice within approximately 5 seconds, it enters the “Sad” state and drops back to the “Lonely” state. Due to the bugginess of the program, it was often difficult for people to make a choice in time to avoid entering the “Sad” state.

## Aftermath and observations

After the conclusion of the art exhibit, I reviewed and analyzed the logs, photographs, and other telemetric data.

The most interesting thing I observed was that on the surface, nobody deliberately chose the option to not play with Charlie, and instead chose to play with it, often multiple times. The majority of people in the hallway chose to ignore the project, especially during passing period. Others looked at the exhibit, and changed directions, perhaps to avoid being filmed.

Similar to the “what is your dream” art exhibit produced by some other student, having to physically stop, take a moment to orient themselves, and interact with the exhibit weeded out people who were naturally inclined towards negative responses. The people who did stop to interact with the exhibit did take a minute or two to try and understand how the exhibit worked, and made multiple attempts to select options despite the bugginess of the program. There did not appear to be a middle ground – either people interacted for extended periods of time with the exhibit, or did not interact at all.

When designing the exhibit, I had perhaps thought that there would be a significant minority of students within the school who had a streak of either curiosity or natural sadism and would attempt selecting the option to not play with Charlie, but this was evidently not the case.

How people initially interacted with the exhibit was interesting. A few students misunderstood how the exhibit worked, and placed their hands on the paper hand cutouts that I placed during 3rd period. 

They often spend approximately 20 seconds puzzling how the exhibit worked, but eventually managed to realize that they needed to step back, standing on the footprints, and that the circles corresponded to their hands. It usually took people a few tries (after entering the “Sad” state) to be able to choose an option relatively quickly. 

Due to either a flaw in the positioning of the feet, or the angle of the Kinect, it was often difficult for people to select options that were on the left side of the screen. For that reason, people tended to want to play Ping-Pong more frequently then tell jokes. Interestingly, even though the “Ping-Pong” option never actually started a game of Ping-Pong, people continued to repeatedly try to play “Ping-Pong”. 

In general, people tended to feel a bit cheated or trolled after interacting with the exhibit, since it never did actually result in a playable game of any sort, feeling perhaps the payoff for interaction was disproportionately small compared amount of time they had put into actually standing in front of exhibit.

Overall, the exhibit was an interesting mixture of confusion, optimism, and disappointment. 
