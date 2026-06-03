"""
@author: xmousset
"""

import sqlite3
import numpy as np
from typing import Any

from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.Animal import AnimalPool, AnimalType, EventTimeLine
from lmtanalysis.Event import deleteEventTimeLineInBase
from lmtanalysis.TaskLogger import TaskLogger

# EVENT NAME (should correspond to the file name)
# ----------------
EVENT_NAME = "Your event"


# DO NOT MODIFY
# ----------------
def flush(connection) -> None:
    """Flush event in database"""
    deleteEventTimeLineInBase(connection, EVENT_NAME)


# YOUR EVENT
# ----------------
def reBuildEvent(
    connection: sqlite3.Connection,
    file: Any | None = None,
    tmin: int | None = None,
    tmax: int | None = None,
    pool: AnimalPool | None = None,
    animalType: AnimalType = AnimalType.MOUSE,
    # your variables here
) -> None:
    """
    Rebuilds the appropriate event for all animals in the database.

    Parameters
    ----------
    connection : sqlite3.Connection
        The SQLite database connection.
    file : Any or None, optional
        The file path or object.
        Can be used by EventTimeLineCached to cache event loading.
        Default is None.
    tmin : int or None, optional
        Start time for detections (in frame). If None, it will load all
        detections from the start.
    tmax : int or None, optional
        End time for detections (in frame). If None, it will load all
        detections until the end.
    pool : AnimalPool or None, optional
        AnimalPool instance (create new one if None, using tmin and tmax).
    animalType : AnimalType, optional
        The appropriate animal type. Default is MOUSE.
    YOUR_VARIABLES : type
        Description of your variables.

    Returns
    -------
    None
    """

    # DO NOT MODIFY
    # ----------------
    # (unless you know what you are doing)
    if pool is None:
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(start=tmin, end=tmax)

    for animal_key in pool.animalDictionary.keys():

        # create a new event timeline for each animal
        # it will be filled with the result of your event detection
        # then saved in database at the end of the process
        your_event_TimeLine = EventTimeLine(
            conn=None,
            eventName=EVENT_NAME,
            idA=animal_key,
            idB=None,
            idC=None,
            idD=None,
            loadEvent=False,
            minFrame=tmin,
            maxFrame=tmax,
        )

        # prepare a dictionary to store the result of your event detection
        # keys of this dictionary should be frame numbers
        # values should be True (do not add False values to the dictionary)
        result = {}

        # example of use:
        # result[f] = True
        # this means your event occur at frame "f"
        # NEVER add a "False" value to the dictionary

        # get the animal object from the pool with the animal key (id)
        animal = pool.animalDictionary[animal_key]

        # ================ YOUR CODE HERE ================

        # example of how to get all frames where the animal was detected
        animal_frames = np.array(sorted(animal.detectionDictionary.keys()))

        # examples of how to skip animals without detections
        if animal_frames.size == 0:
            continue

        # example of how to get massX position of the animal detections
        # in a numpy array and with the same order as animal_frames
        massX = np.array(
            [animal.detectionDictionary.get(f).massX for f in animal_frames]
        )

        # example of how to compute speed along X axis
        frame_gaps = np.diff(animal_frames)
        vx = np.zeros_like(massX)
        vx[1:] = np.diff(massX) / frame_gaps

        # example of how to get the frames corresponding to an existing event
        stop_frames = EventTimeLine(
            conn=connection,
            eventName="Stop",
            idA=animal_key,
        ).getDictionary()

        # ================ END OF YOUR CODE ================

        # DO NOT MODIFY
        # ----------------
        # store your result in the event timeline and save it in database
        your_event_TimeLine.reBuildWithDictionary(result)
        your_event_TimeLine.endRebuildEventTimeLine(connection)

    # DO NOT MODIFY
    # ----------------
    # log process for debugging and record keeping
    t = TaskLogger(connection)
    if tmin is None or tmax is None:
        t.addLog(f"Build Event {EVENT_NAME} (tmin or tmax is None)")
    else:
        t.addLog(f"Build Event {EVENT_NAME}", tmin=tmin, tmax=tmax)
    print(f"Rebuild {EVENT_NAME} event finished.")
