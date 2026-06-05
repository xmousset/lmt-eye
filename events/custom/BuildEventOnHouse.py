"""
@author: Fab
"""

import sqlite3
from typing import Any

from lmtanalysis.TaskLogger import TaskLogger
from lmtanalysis.Event import deleteEventTimeLineInBase
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.Animal import Animal, AnimalPool, AnimalType, EventTimeLine
from lmtanalysis.Measure import oneSecond, oneMinute, oneHour, oneDay, oneWeek

# EVENT INFO
# ----------------

EVENTS_NAME: list[str] = ["onHouse"]

EVENTS_DESCRIPTION: str = """
    The animal is on top of the house. Detected when the animal is in the center zone
    and meets height thresholds: massZ > 128, frontZ > 30. This indicates the animal has
    climbed onto the house structure.
"""


# Rebuild function
# ----------------
def reBuildEvent(
    connection: sqlite3.Connection,
    file: Any | None = None,
    tmin: int | None = None,
    tmax: int | None = None,
    pool: AnimalPool | None = None,
    animalType: AnimalType = AnimalType.MOUSE,
) -> None:

    # Parameters
    # ----------------
    mass_z_threshold = 128  # minimum massZ to be on house
    head_z_threshold = 30  # minimum frontZ to be on house
    min_event_length = 5  # minimum frames for event
    merging_gap = 30  # merge events that are separated by 30 frames or less

    # Events creation
    # ----------------
    if pool is None:
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(start=tmin, end=tmax, lightLoad=False)
    # lightLoad=False needed because we access frontZ and massZ

    for animal in pool.animalDictionary.values():

        onHouse_TL = EventTimeLine(
            conn=None,
            eventName=EVENTS_NAME[0],
            idA=animal.baseId,
            loadEvent=False,
            minFrame=tmin,
            maxFrame=tmax,
        )

        # Get the Center Zone event dictionary to filter detections
        center_zone_TL = EventTimeLineCached(
            connection=connection,
            file=file,
            eventName="Center Zone",
            idA=animal.baseId,
        )
        center_zone_dictionary = center_zone_TL.getDictionary()

        result = {}

        sorted_detections = sorted(animal.detectionDictionary.items())

        for f, detect in sorted_detections:
            # Only consider frames in Center Zone
            if f not in center_zone_dictionary:
                continue

            # Check height thresholds
            mass_ok = detect.massZ > mass_z_threshold
            head_ok = detect.frontZ > 0 and detect.frontZ > head_z_threshold

            # Mark as onHouse if both conditions met
            if mass_ok and head_ok:
                result[f] = True

        onHouse_TL.reBuildWithDictionary(result)
        onHouse_TL.removeEventsBelowLength(min_event_length)
        onHouse_TL.mergeCloseEvents(merging_gap)
        onHouse_TL.endRebuildEventTimeLine(connection)

    # Do not modify
    # ----------------
    # log process for debugging and record keeping
    t = TaskLogger(connection)
    for event_name in EVENTS_NAME:
        if tmin is None or tmax is None:
            t.addLog(f"Build Event '{event_name}' (tmin or tmax is None)")
        else:
            t.addLog(f"Build Event '{event_name}'", tmin=tmin, tmax=tmax)
    print(f"Event rebuilding finished: '{"', '".join(EVENTS_NAME)}'")


# Do not modify
# ----------------
def flush(connection) -> None:
    """Flush event in database"""
    for event_name in EVENTS_NAME:
        deleteEventTimeLineInBase(connection, event_name)
