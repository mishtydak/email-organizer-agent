from dataclasses import dataclass
from datetime import (
    datetime,
    timedelta,
    time
)
import re
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo("Asia/Kolkata")


@dataclass
class ProposedSlot:
    start: datetime
    end: datetime


DAYS_OF_WEEK = {
    "monday": 0, "tuesday": 1, "wednesday": 2,
    "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
}

def resolve_datetime(day_str, time_str, reference_date=None):
    if reference_date is None:
        reference_date = datetime.now().date()
        
    target_weekday = DAYS_OF_WEEK.get(day_str.lower(), reference_date.weekday())
    days_ahead = target_weekday - reference_date.weekday()
    if days_ahead < 0 or (days_ahead == 0 and day_str.lower() in DAYS_OF_WEEK):
        # We assume if they mention a weekday it is usually in the future
        # e.g., if today is Friday, and they say Friday, they probably mean next Friday.
        # But for tests we'll just advance to next week if days_ahead < 0. If 0, let's keep it today.
        if days_ahead < 0:
            days_ahead += 7
            
    resolved_date = reference_date + timedelta(days=days_ahead)
    
    match = re.match(r"(\d+)(?::(\d+))?\s*(am|pm)?", time_str.lower())
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        ampm = match.group(3)
        if ampm == "pm" and hour < 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0
        resolved_time = time(hour, minute)
    else:
        resolved_time = time(9, 0)
        
    return datetime.combine(resolved_date, resolved_time).replace(tzinfo=LOCAL_TZ)


def overlaps(
    slot_start,
    slot_end,
    busy_start,
    busy_end
):
    return (
        slot_start < busy_end
        and slot_end > busy_start
    )

def find_available_slots(
    busy_periods,
    start_date,
    days=5,
    duration_minutes=30,
    work_start_hour=9,
    work_end_hour=17
):
    slots = []

    for day_offset in range(days):

        current_date = (
            start_date
            + timedelta(days=day_offset)
        )

        # Skip Saturday and Sunday
        if current_date.weekday() >= 5:
            continue

        current_time = datetime.combine(
            current_date,
            time(work_start_hour, 0)
        ).replace(tzinfo=LOCAL_TZ)

        work_end = datetime.combine(
            current_date,
            time(work_end_hour, 0)
        ).replace(tzinfo=LOCAL_TZ)

        while (
            current_time
            + timedelta(minutes=duration_minutes)
            <= work_end
        ):

            slot_end = (
                current_time
                + timedelta(minutes=duration_minutes)
            )

            is_busy = False

            for busy in busy_periods:

                busy_start = datetime.fromisoformat(
                    busy["start"].replace("Z", "+00:00")
                )

                busy_end = datetime.fromisoformat(
                    busy["end"].replace("Z", "+00:00")
                )

                if overlaps(
                    current_time,
                    slot_end,
                    busy_start,
                    busy_end
                ):
                    is_busy = True
                    break

            if not is_busy:
                slots.append(
                    ProposedSlot(
                        start=current_time,
                        end=slot_end
                    )
                )

            current_time += timedelta(minutes=30)

    return slots


def propose_meeting_slots(
    calendar_connector,
    start_date,
    days=5,
    duration_minutes=30,
    number_of_slots=5
):
    # Backward compatibility
    return propose_meeting_slots_with_preference(
        calendar_connector, start_date, None, None, days, duration_minutes, number_of_slots
    )[0]


def propose_meeting_slots_with_preference(
    calendar_connector,
    start_date,
    proposed_date_str=None,
    proposed_time_str=None,
    days=5,
    duration_minutes=30,
    number_of_slots=5
):
    time_min = datetime.combine(start_date, time(0, 0)).replace(tzinfo=LOCAL_TZ)
    time_max = time_min + timedelta(days=days)

    busy_periods = calendar_connector.get_busy_periods(time_min, time_max)

    requested_slot = None
    requested_status = None

    if proposed_date_str and proposed_time_str:
        requested_dt = resolve_datetime(proposed_date_str, proposed_time_str, start_date)
        req_end = requested_dt + timedelta(minutes=duration_minutes)

        is_busy = False
        for busy in busy_periods:
            busy_start = datetime.fromisoformat(busy["start"].replace("Z", "+00:00"))
            busy_end = datetime.fromisoformat(busy["end"].replace("Z", "+00:00"))

            # Native aware datetime comparison works perfectly
            if overlaps(requested_dt, req_end, busy_start, busy_end):
                is_busy = True
                break

        requested_slot = ProposedSlot(start=requested_dt, end=req_end)
        requested_status = "BUSY" if is_busy else "AVAILABLE"

    slots = []
    if requested_slot and requested_status == "AVAILABLE":
        slots.append(requested_slot)

    if requested_slot:
        target_dates = [requested_slot.start.date()]
        for d in range(days):
            candidate = start_date + timedelta(days=d)
            if candidate != requested_slot.start.date():
                target_dates.append(candidate)
    else:
        target_dates = [start_date + timedelta(days=d) for d in range(days)]

    for d in target_dates:
        if d.weekday() >= 5:
            continue

        current_time = datetime.combine(d, time(9, 0)).replace(tzinfo=LOCAL_TZ)
        work_end = datetime.combine(d, time(17, 0)).replace(tzinfo=LOCAL_TZ)

        day_slots = []
        while current_time + timedelta(minutes=duration_minutes) <= work_end:
            slot_end = current_time + timedelta(minutes=duration_minutes)

            if requested_slot and current_time == requested_slot.start:
                current_time += timedelta(minutes=30)
                continue

            is_busy = False
            for busy in busy_periods:
                busy_start = datetime.fromisoformat(busy["start"].replace("Z", "+00:00"))
                busy_end = datetime.fromisoformat(busy["end"].replace("Z", "+00:00"))

                if overlaps(current_time, slot_end, busy_start, busy_end):
                    is_busy = True
                    break

            if not is_busy:
                day_slots.append(ProposedSlot(start=current_time, end=slot_end))

            current_time += timedelta(minutes=30)

        if requested_slot and d == requested_slot.start.date():
            day_slots.sort(key=lambda s: abs((s.start - requested_slot.start).total_seconds()))

        for s in day_slots:
            if len(slots) >= number_of_slots:
                break
            slots.append(s)

        if len(slots) >= number_of_slots:
            break

    return slots, requested_status