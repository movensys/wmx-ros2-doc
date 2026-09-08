Robopoly Game Guide
===================

Robopoly is a simple board game played against the robot. Users drive their
turns by voice; the manipulator reads the dice and moves the pieces. This page
describes the warm-up, the turn flow, and the full game logic. For how to
launch the demo, see :doc:`robopoly_game`.

Warm-up
-------

1. Open the **web-based manipulator controller** at ``localhost:8000``.

   - Tune the velocity and acceleration to **0.8--0.9** (recommended).
   - Press **Go To Init** and watch the speed of the manipulator.

2. Open the **Robopoly game** at ``localhost:7999``.

   - After following :doc:`robopoly_game`, open Chrome and go to
     ``localhost:7999``.
   - Click the **Game mode** button in the upper-right corner.
   - Hold down the **X** key and say something to warm up the LLM and
     Text-to-Speech (TTS) AI models.

You are now ready to run the Robopoly demo.

Game Process
------------

User Turn
~~~~~~~~~

1. The user turn starts. The user can choose one of two actions: **check the
   game status** or **see the dice number**.

   Hold down the **Z** key, say the action, and release the **Z** key.

2. If the user says **check the game status**, the user's money and turn
   information pop up on the game screen.

3. If the user says **see the dice number**, the manipulator reads the dice and
   moves the user's piece on the board based on the dice number.

4. If the user arrives at a property not owned by another user, the user can
   choose one of the following actions: **Buy land**, **Buy house**,
   **Buy hotel**, or **Skip**.

   Hold down the **Z** key, say the action, and release the **Z** key.

5. Other cases follow the game logic -- see `Game Explanation`_.

The user turn ends.

Robot Turn
~~~~~~~~~~

1. The robot automatically rolls the dice and reflects the dice number on the
   board.
2. The robot chooses the proper building based on its money.
3. Other cases follow the game logic -- see `Game Explanation`_.

The robot turn ends.

Turns alternate between the user and the robot until the game ends -- see
`Game Explanation`_.

Game Explanation
----------------

Environment
~~~~~~~~~~~

Two users start with $500 each.

Rules
~~~~~

- Both users' pieces start at the **GO** position.
- Move each piece based on the dice number.
- **IN THE DESERT ISLAND** is not counted in the movable cells; it can only be
  reached by **GO TO DESERT ISLAND**.
- When a user arrives at a new property, the user can take one of the following
  actions: **Skip**, **Buy land**, **Buy house**, or **Buy hotel**.
- Valid property cells: BOSTON, SEOUL, TAIPEI, SHANGHAI, TOKYO, BUSAN, NEWYORK,
  LONDON.
- When a user arrives at an opponent-owned property, the user pays the owner:

  - Land (no building): $150
  - House: $300
  - Hotel: $450

Special Cases
~~~~~~~~~~~~~

- **IN THE DESERT ISLAND** -- the user can only escape the cell by rolling a 6.
- **ELECTRIC COMPANY** -- the user can **Skip** or **Buy land**. The penalty is
  the same as a normal land property.
- **NON-FREE PARKING** -- the user loses $100.
- **GO** -- the user gains $100.
- **CHANCE** -- the user shows a handwritten card to the manipulator camera.
  Card examples: $200, $100, $0 (Sorry), and -$150.

End Game
~~~~~~~~

- When a user goes bankrupt, the game ends and the opponent wins.
- After moving around the board twice, the game ends and the richer user wins.

Board
-----

.. The board layout / image goes here.
