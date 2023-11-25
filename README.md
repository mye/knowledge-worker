# Knowledge Worker

> :warning: **Warning:** This idea is unfinished, unclear, experimental and irregularly updated.

## What's a knowledge worker?

Someone said "Doing with images makes symbols". As in, for example children learning visually and constructing a symbolic system cf. etoys. The music is not in the piano. OK. What is the "music" of a computer? The symbols? What is actually important? A copilot answer:

> The symbols or the meaning? The meaning is not in the symbols. The meaning is in the mind of the person who reads the symbols. The symbols are just a way to communicate the meaning. The symbols are not the meaning. The symbols are not the music. The symbols are not the knowledge. The symbols are not the information. The symbols are not the data. The symbols are not the content. The symbols are not the message. The

Maybe this trouble arises because "a computer" doesn't exist in the following sense:

> Suppose, for example, I am talking about a fishpond, and want to call it a whole. To be accurate about it in a mathematical theory, I want to be able to draw a precious boundary around this whole, and say for each point in space whether it is part of this set of points or not. But this is very hard to do. Obviously the water is part of the fishpond. What about the concrete it is made of? .. the air which is just about the pond? … the pipes bringing in the water? These are uncomfortable questions … The pond does exist. Our trouble is that we don’t know how to define it exactly. But the trouble comes from referring to it as a ‘whole.’ That kind of terminology seems to make it necessary for me to draw an exact boundary … That is the mistake -- _Christopher Alexander – The Nature of Order – Book 1: The Phenomenon of Life_

## (Bad) Ideas

### Voicelog

Run speech to text and save it to a db. An agent can read that voicelog and take on goals of the speaker.

Ensure that running the program multiple times doesn't duplicate entries.
Validate that all timestamps are correctly converted to UNIX format in milliseconds.
Confirm that no lines containing [silence] or repeated content make it into the database.
Check that both start and end timestamps are accurately captured for each entry.
Confirm that the unique index effectively prevents duplicate entries based on start_timestamp, end_timestamp, and content.

pip install -e
python -m build
python3 -m pip install build
