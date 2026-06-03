"""
@creation: 26-01-2026
@last update: 28-01-2026
@author: xmousset
"""

from pathlib import Path
import importlib.util
from types import ModuleType
from typing import Optional

from events.official import (
    BuildEventApproachContact,
    BuildEventApproachRear,
    BuildEventCenterPeripheryLocation,
    BuildEventDetection,
    BuildEventExclusiveCleanOralOralSideSideNoseAnogenitalContact,
    BuildEventExclusiveMoveStopIsolated,
    BuildEventExclusiveUndetected,
    BuildEventFlickering,
    BuildEventFloorSniffing,
    BuildEventFollowZone,
    BuildEventGetAway,
    BuildEventGroup2,
    BuildEventGroup3,
    BuildEventGroup3MakeBreak,
    BuildEventGroup4,
    BuildEventGroup4MakeBreak,
    BuildEventHouse,
    BuildEventHuddling,
    BuildEventInCorner,
    BuildEventLongChase,
    BuildEventMove,
    BuildEventMoveSpeedCategories,
    BuildEventMoveSpeedCategories2,
    BuildEventNest3,
    BuildEventNest4,
    BuildEventObjectSniffingNor,
    BuildEventObjectSniffingNorAcquisitionWithConfig,
    BuildEventObjectSniffingNorTestWithConfig,
    BuildEventOnHouse,
    BuildEventOralGenitalContact,
    BuildEventOralOralContact,
    BuildEventOralSideSequence,
    BuildEventOtherContact,
    BuildEventPassiveAnogenitalSniff,
    BuildEventRear5,
    BuildEventRearCenterPeriphery,
    BuildEventSAP,
    BuildEventSideBySide,
    BuildEventSideBySideOpposite,
    BuildEventSocialApproach,
    BuildEventSocialEscape,
    BuildEventStop,
    BuildEventTrain2,
    BuildEventTrain3,
    BuildEventTrain4,
    BuildEventWallJump,
    BuildEventWaterPoint,
)

OFFICIAL_EVENTS: dict[str, ModuleType | str | None] = {
    "Approach": None,
    "Approach contact": BuildEventApproachContact,
    "Approach rear": BuildEventApproachRear,
    "ASSOCIATION": None,
    "badIdentity": None,
    "badOrientation": None,
    "badSegmentation": None,
    "Behind": None,
    "Break contact": None,
    "Center Zone": BuildEventCenterPeripheryLocation,
    "Contact": None,
    "Corner": BuildEventInCorner,
    "Corner 0": "Corner",
    "Corner 1": "Corner",
    "Corner 2": "Corner",
    "Corner 3": "Corner",
    "coucou": None,
    "Detection": BuildEventDetection,
    "Escape": None,
    "event": None,
    "Flickering": BuildEventFlickering,
    "Floor sniffing": BuildEventFloorSniffing,
    "Follow": None,
    "FollowZone": BuildEventFollowZone,
    "Get away": BuildEventGetAway,
    "Group 3 break": BuildEventGroup3MakeBreak,
    "Group 3 make": "Group 3 break",
    "Group 4 break": BuildEventGroup4MakeBreak,
    "Group 4 make": "Group 4 break",
    "Group2": BuildEventGroup2,
    "Group3": BuildEventGroup3,
    "Group4": BuildEventGroup4,
    "Head detected": None,
    "Huddling": BuildEventHuddling,
    "in house corner": BuildEventHouse,
    "longChase": BuildEventLongChase,
    "Look down": None,
    "MACHINE LEARNING": None,
    "manualContact": None,
    "manualOralGenital": None,
    "manualOralOralContact": None,
    "manualSideSideOpposite": None,
    "manualSideSideSame": None,
    "Move": BuildEventMove,
    "Move high speed": BuildEventMoveSpeedCategories2,
    "Move in contact": "Move",
    "Move isolated": "Move",
    "Nest3_": BuildEventNest3,
    "Nest4_": BuildEventNest4,
    "onHouse": BuildEventOnHouse,
    "Oral-genital Contact": BuildEventOralGenitalContact,
    "Oral-oral Contact": BuildEventOralOralContact,
    "Other contact": BuildEventOtherContact,
    "over house": "in house corner",
    "Passive oral-genital Contact": BuildEventPassiveAnogenitalSniff,
    "Periphery Zone": "Center Zone",
    "Rear at periphery": BuildEventRearCenterPeriphery,
    "Rear in centerWindow": "Rear at periphery",
    "Rear in contact": BuildEventRear5,
    "Rear isolated": "Rear in contact",
    "Rearing": None,
    "RFID ASSIGN ANONY-MOUS TRACK": None,
    "RFID MATCH": None,
    "RFID MISMATCH": None,
    "SAP": BuildEventSAP,
    "seq oral geni - oral oral": "seq oral oral - oral genital",
    "seq oral oral - oral genital": BuildEventOralSideSequence,
    "Side by side Contact": BuildEventSideBySide,
    "Side by side Contact, opposite way": BuildEventSideBySideOpposite,
    # "SniffLeft": BuildEventObjectSniffingNor,
    # "SniffRight": "SniffLeft",
    "Social approach": BuildEventSocialApproach,
    "Social escape": BuildEventSocialEscape,
    "Stop": None,
    "Stop in contact": BuildEventStop,
    "Stop isolated": BuildEventStop,
    "Train2": BuildEventTrain2,
    "Train3": BuildEventTrain3,
    "Train4": BuildEventTrain4,
    "WallJump": BuildEventWallJump,
    "Water Stop": BuildEventWaterPoint,
    "Water Zone": "Water Stop",
}


def _load_custom_events() -> dict[str, ModuleType]:
    """
    Load all custom event modules from events/custom directory.
    (Similar to OFFICIAL_EVENTS but for custom events)

    Returns
    -------
    dict[str, ModuleType]
        Dictionary with EVENT_NAME as key and module as value.
        Example: {"Speed": <module>, "Rearing": <module>, ...}
    """
    print("Loading custom events...")
    custom_events_dir = Path(__file__).parent / "custom"
    events_dict = {}

    if not custom_events_dir.exists():
        print(f"Warning: {custom_events_dir} does not exist")
        return events_dict

    # Iterate through all .py files in events/custom
    for file_path in custom_events_dir.glob("BuildEvent*.py"):

        try:
            # Load module dynamically
            spec = importlib.util.spec_from_file_location(
                file_path.stem,
                file_path,
            )
            assert spec is not None and spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get EVENT_NAME from module and add to dict
            if hasattr(module, "EVENT_NAME"):
                event_name = module.EVENT_NAME
                events_dict[event_name] = module
                print(f"✓ {event_name}")
            else:
                print(
                    f"⚠ Warning: {file_path.name} has no EVENT_NAME attribute"
                )

        except Exception as e:
            print(f"✗ Loading error: {file_path.name}\n{e}")

    print(f"Finished loading custom events. Total loaded: {len(events_dict)}")
    return events_dict


# Load custom events once at module import time
CUSTOM_EVENTS: dict[str, ModuleType] = _load_custom_events()


def get_official_events_name() -> set[str]:
    """Return a set of official event names."""
    return set(OFFICIAL_EVENTS.keys())


def get_custom_events_name() -> set[str]:
    """Return a set of custom event names."""
    return set(CUSTOM_EVENTS.keys())


def get_modules_from_events_name(names: list[str] | set[str]):
    """Get a set of unique modules associated with a list of event names."""
    modules: set[ModuleType] = set()

    if isinstance(names, list):
        names = set(names)

    official_events = get_official_events_name()
    custom_events = get_custom_events_name()

    for event_name in names:
        module = None

        if event_name in official_events:
            module = OFFICIAL_EVENTS.get(event_name, None)
            if isinstance(module, str):
                module = OFFICIAL_EVENTS.get(module, None)

        elif event_name in custom_events:
            module = CUSTOM_EVENTS.get(event_name, None)

        if isinstance(module, ModuleType):
            modules.add(module)

    return modules
