"""
Created on 23 mai 2023

@author: eye
@modified on by xmousset
"""

import sqlite3
import numpy as np
from typing import Any

from lmtanalysis.TaskLogger import TaskLogger
from lmtanalysis.Parameters import get_scale_cm_over_px
from lmtanalysis.Event import deleteEventTimeLineInBase
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.Animal import Animal, AnimalPool, AnimalType, EventTimeLine
from lmtanalysis.Measure import oneSecond, oneMinute, oneHour, oneDay, oneWeek

# EVENT INFO
# ----------------

EVENTS_NAME: list[str] = [
    "Corner",
    "Corner NW",
    "Corner NE",
    "Corner SW",
    "Corner SE",
]

EVENTS_DESCRIPTION: str = """
    Detects when the animal is in one of the arena corners (NW, NE, SW, SE).
    Each corner is a 5 cm radius circle.
    Events require minimum 6-frame duration (0.2s), with gaps ≤3 frames merged.
"""


# DO NOT MODIFY
# ----------------
def flush(connection) -> None:
    """Flush event in database"""
    for event_name in EVENTS_NAME:
        deleteEventTimeLineInBase(connection, event_name)


def reBuildEvent(
    connection: sqlite3.Connection,
    file: Any | None = None,
    tmin: int | None = None,
    tmax: int | None = None,
    pool: AnimalPool | None = None,
    animalType: AnimalType = AnimalType.MOUSE,
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

    Returns
    -------
    None
    """

    # Parameters
    # ----------------
    cm_over_px = get_scale_cm_over_px(animalType)

    corners_coord = {
        "NW": (114, 63),
        "NE": (398, 63),
        "SE": (398, 353),
        "SW": (114, 353),
    }  # in px

    radius = 5 / cm_over_px  # 5 cm radius around the corner
    min_duration_in_corner = 6 * oneSecond  # minimum duration for valid event
    merging_gap = 3  # merge events that are separated by 3 frames or less

    # Events creation
    # ----------------
    if pool is None:
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(start=tmin, end=tmax, lightLoad=True)

    for animal in pool.animalDictionary.values():

        result_corner: dict[str, dict[int, bool]] = {}
        cornerTimeLine: dict[str, EventTimeLine] = {}

        for k in ["NW", "NE", "SW", "SE"]:
            result_corner[k] = {}
            cornerTimeLine[k] = EventTimeLine(
                conn=None,
                eventName=f"{EVENTS_NAME[0]} {k}",
                idA=animal.baseId,
                idB=None,
                idC=None,
                idD=None,
                loadEvent=False,
                minFrame=tmin,
                maxFrame=tmax,
            )

        for f in sorted(animal.detectionDictionary.keys()):
            for k in ["NW", "NE", "SW", "SE"]:
                distanceToEventLocation = animal.getDistanceToPoint(
                    f,
                    corners_coord[k][0],
                    corners_coord[k][1],
                )
                if distanceToEventLocation == None:
                    print("Distance cannot be computed.")
                    break
                if distanceToEventLocation <= radius:
                    result_corner[k][f] = True
                    break

        # Must be kept
        # ----------------
        for k in ["NW", "NE", "SW", "SE"]:
            cornerTimeLine[k].reBuildWithDictionary(result_corner[k])
            cornerTimeLine[k].removeEventsBelowLength(min_duration_in_corner)
            cornerTimeLine[k].mergeCloseEvents(merging_gap)
            cornerTimeLine[k].endRebuildEventTimeLine(connection)

    # Must be kept
    # ----------------
    # log process for debugging and record keeping
    f = TaskLogger(connection)
    for event_name in EVENTS_NAME:
        if tmin is None or tmax is None:
            f.addLog(f"Build Event {event_name} (tmin or tmax is None)")
        else:
            f.addLog(f"Build Event {event_name}", tmin=tmin, tmax=tmax)
    print(f"Event rebuilding finished: {EVENTS_NAME}")
