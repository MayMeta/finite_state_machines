# Toy Problem

## Setting

Let’s say we work for a large candy manufacturer.
In one production line they create lollipops in one of 2 flavors: Strawberry and Lemon.
The production line is supposed to alternately output one Strawberry-flavored lollipop,
then one Lemon-flavored one, then another one Strawberry-flavored lollipop, and so on and so forth.
Using a single letter notation it should output something like this:  
`[S, L, S, L, S, L, ...]`

Now, in some cases, due to some fluke there can be a case where two lollipops of the same flavor
appear one after the other, and that’s fine.  
`[S, L, S, S, L, S, L, ...]`

However, if three lollipops of the same flavor appear in a row, that likely means there is some serious problem,
and we need to call an Engineer to review the machines.  
`[S, L, L, L] # problem detected`

## Task

Build a State Machine which will:

A. Take some form of input  
- Input source can be from keyboard, file, or something else;  
- The input should be some representation of the series of flavors;  

B. Detect when the Production line output three consecutive lollipops of the same flavor  
- It should do so every time this happens;  
- However, once it recognized an error in the production line, it should not treat additional consecutive output
of the same flavor as another error. For instance, in the following sequence it will only detect three (3) errors.
Elements of the input sequence that trigger the error are market with an asterisk (\*):  
`[S, L, L, L*, L, S, S, S*, S, S, S, L, L, L*, ...]`  
- Output an appropriate error message to the console when each error is detected.  

## Persistence

Some State Machines are expected to run for prolonged periods of time - potentially even indefinitely.
However, it is common that the system needs to be shut down for maintenance or, say, crashes due to an internal error.
This means that we need some way to store the current state of the system on disk and then to restore the system
to a previously-saved state during system load.

Our toy problem solution should demonstrate this form of persistence.
