#!/usr/bin/env python3
"""
Dynamic Timetable Scheduler - Python Interface
File: timetable_scheduler.py

This module provides a Python interface to interact with a Prolog-based
timetable scheduling system, or fallbacks to mock data if Prolog is unavailable.
"""

import sys
from typing import List, Dict, Optional
from dataclasses import dataclass
from tabulate import tabulate
import json

try:
    from pyswip import Prolog
    PYSWIP_AVAILABLE = True
except ImportError:
    PYSWIP_AVAILABLE = False
    print("Warning: pyswip not installed. Install with: pip install pyswip")
    print("Running in demo mode with mock data.")


@dataclass
class Course:
    """Represents a course in the timetable system."""
    id: str
    name: str
    teacher_id: str
    teacher_name: str
    duration: int
    room_type: str


@dataclass
class TimeSlot:
    """Represents a time slot in the timetable system."""
    id: str
    day: str
    start_time: int
    end_time: int
    duration: int


@dataclass
class Room:
    """Represents a room in the timetable system."""
    id: str
    room_type: str
    capacity: int


@dataclass
class ScheduleEntry:
    """Represents a single entry in the timetable."""
    course: Course
    time_slot: TimeSlot
    room: Room


class TimetableScheduler:
    """Main class for timetable scheduling."""

    def __init__(self, prolog_file: str = "timetable_scheduler.pl") -> None:
        """Initialize scheduler and load data."""
        self.prolog_file = prolog_file
        self.prolog_available = False
        self.courses: Dict[str, Course] = {}
        self.time_slots: Dict[str, TimeSlot] = {}
        self.rooms: Dict[str, Room] = {}
        self.schedule: List[ScheduleEntry] = []

        if PYSWIP_AVAILABLE:
            self.prolog = Prolog()
            try:
                self.prolog.consult(prolog_file)
                self.prolog_available = True
                print(f"Successfully loaded Prolog file: {prolog_file}")
            except Exception as e:
                print(f"Error loading Prolog file: {e}")

        self._load_data()

    def _load_data(self) -> None:
        """Load data either from Prolog or mock data."""
        if self.prolog_available:
            self._load_from_prolog()
        else:
            self._load_mock_data()

    def _load_from_prolog(self) -> None:
        """Load courses, time slots, and rooms from Prolog knowledge base."""
        try:
            for sol in self.prolog.query("get_course_details(CourseID, CourseName, TeacherName, Duration, RoomType)"):
                course_id = sol["CourseID"]
                self.courses[course_id] = Course(
                    id=course_id,
                    name=sol["CourseName"],
                    teacher_id="",  # Not provided, can extend if needed
                    teacher_name=sol["TeacherName"],
                    duration=sol["Duration"],
                    room_type=sol["RoomType"],
                )

            for sol in self.prolog.query("get_time_details(SlotID, Day, StartTime, EndTime)"):
                slot_id = sol["SlotID"]
                start = sol["StartTime"]
                end = sol["EndTime"]
                self.time_slots[slot_id] = TimeSlot(
                    id=slot_id,
                    day=sol["Day"],
                    start_time=start,
                    end_time=end,
                    duration=(end - start) // 100,  # simplistic duration calc in hours
                )

            for sol in self.prolog.query("get_room_details(RoomID, RoomType, Capacity)"):
                room_id = sol["RoomID"]
                self.rooms[room_id] = Room(
                    id=room_id,
                    room_type=sol["RoomType"],
                    capacity=sol["Capacity"],
                )

        except Exception as e:
            print(f"Error loading data from Prolog: {e}")
            print("Falling back to mock data.")
            self._load_mock_data()

    def _load_mock_data(self) -> None:
        """Load mock data if Prolog is unavailable."""
        self.courses = {
            "cs101": Course("cs101", "Computer Science 101", "t001", "Dr. Smith", 2, "computer_lab"),
            "cs102": Course("cs102", "Data Structures", "t002", "Prof. Johnson", 2, "computer_lab"),
            "math101": Course("math101", "Calculus I", "t003", "Dr. Brown", 1, "classroom"),
            "math102": Course("math102", "Linear Algebra", "t004", "Prof. Davis", 2, "classroom"),
            "phy101": Course("phy101", "Physics I", "t005", "Dr. Wilson", 2, "physics_lab"),
        }

        self.time_slots = {
            "slot1": TimeSlot("slot1", "monday", 800, 900, 1),
            "slot2": TimeSlot("slot2", "monday", 900, 1000, 1),
            "slot3": TimeSlot("slot3", "monday", 1000, 1200, 2),
            "slot4": TimeSlot("slot4", "tuesday", 800, 900, 1),
            "slot5": TimeSlot("slot5", "tuesday", 1000, 1200, 2),
        }

        self.rooms = {
            "r001": Room("r001", "computer_lab", 30),
            "r002": Room("r002", "classroom", 40),
            "r003": Room("r003", "physics_lab", 20),
        }

    def generate_schedule(self) -> bool:
        """Generate the timetable schedule."""
        if self.prolog_available:
            return self._generate_prolog_schedule()
        else:
            return self._generate_mock_schedule()

    def _generate_prolog_schedule(self) -> bool:
        """Generate schedule using Prolog."""
        try:
            list(self.prolog.query("clear_schedule"))
            solutions = list(self.prolog.query("generate_optimal_timetable"))

            if not solutions:
                return False

            self.schedule.clear()
            for sol in self.prolog.query("get_schedule(Schedule)"):
                for course_id, slot_id, room_id in sol["Schedule"]:
                    if course_id in self.courses and slot_id in self.time_slots and room_id in self.rooms:
                        self.schedule.append(ScheduleEntry(
                            course=self.courses[course_id],
                            time_slot=self.time_slots[slot_id],
                            room=self.rooms[room_id],
                        ))
            return True

        except Exception as e:
            print(f"Error generating Prolog schedule: {e}")
            return False

    def _generate_mock_schedule(self) -> bool:
        """Generate a simple mock schedule."""
        self.schedule = [
            ScheduleEntry(self.courses["cs101"], self.time_slots["slot3"], self.rooms["r001"]),
            ScheduleEntry(self.courses["math101"], self.time_slots["slot1"], self.rooms["r002"]),
            ScheduleEntry(self.courses["phy101"], self.time_slots["slot5"], self.rooms["r003"]),
        ]
        return True

    def display_schedule(self) -> None:
        """Display the schedule in a table format."""
        if not self.schedule:
            print("No schedule generated yet. Run generate_schedule() first.")
            return

        table_data = [
            [
                e.course.name,
                e.course.teacher_name,
                e.time_slot.day.capitalize(),
                self._format_time(e.time_slot.start_time),
                self._format_time(e.time_slot.end_time),
                e.room.id,
                e.room.room_type.replace('_', ' ').title(),
            ]
            for e in self.schedule
        ]

        headers = ["Course", "Teacher", "Day", "Start", "End", "Room", "Room Type"]
        print("\n" + "="*80)
        print("GENERATED TIMETABLE")
        print("="*80)
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print("="*80)

    def display_schedule_by_day(self) -> None:
        """Display schedule grouped by day."""
        if not self.schedule:
            print("No schedule generated yet.")
            return

        days: Dict[str, List[ScheduleEntry]] = {}
        for entry in self.schedule:
            day = entry.time_slot.day.capitalize()
            days.setdefault(day, []).append(entry)

        print("\n" + "="*80)
        print("TIMETABLE BY DAY")
        print("="*80)

        for day in sorted(days):
            print(f"\n{day.upper()}:")
            print("-" * 40)
            entries_sorted = sorted(days[day], key=lambda e: e.time_slot.start_time)
            table_data = [
                [
                    self._format_time(e.time_slot.start_time),
                    self._format_time(e.time_slot.end_time),
                    e.course.name,
                    e.course.teacher_name,
                    e.room.id,
                ]
                for e in entries_sorted
            ]

            headers = ["Start", "End", "Course", "Teacher", "Room"]
            print(tabulate(table_data, headers=headers, tablefmt="simple"))

    def check_conflicts(self) -> List[str]:
        """Check for scheduling conflicts among teachers and rooms."""
        conflicts = []
        teacher_slots: Dict[str, set] = {}
        room_slots: Dict[str, set] = {}

        for entry in self.schedule:
            teacher = entry.course.teacher_name
            room = entry.room.id
            slot_key = f"{entry.time_slot.day}_{entry.time_slot.start_time}"

            # Check teacher conflicts
            if slot_key in teacher_slots.setdefault(teacher, set()):
                conflicts.append(f"Teacher {teacher} has overlapping classes at {slot_key}")
            else:
                teacher_slots[teacher].add(slot_key)

            # Check room conflicts
            if slot_key in room_slots.setdefault(room, set()):
                conflicts.append(f"Room {room} has overlapping bookings at {slot_key}")
            else:
                room_slots[room].add(slot_key)

        return conflicts

    def get_statistics(self) -> Dict[str, int]:
        """Return statistics about the generated schedule."""
        if not self.schedule:
            return {}

        stats = {
            "total_courses": len(self.courses),
            "scheduled_courses": len(self.schedule),
            "total_rooms": len(self.rooms),
            "used_rooms": len({e.room.id for e in self.schedule}),
            "total_time_slots": len(self.time_slots),
            "used_time_slots": len({e.time_slot.id for e in self.schedule}),
            "conflicts": len(self.check_conflicts()),
        }
        return stats

    @staticmethod
    def _format_time(time_int: int) -> str:
        """Format integer time (e.g. 1300) to HH:MM string."""
        hours, minutes = divmod(time_int, 100)
        return f"{hours:02d}:{minutes:02d}"

    def export_schedule(self, filename: str = "timetable.json") -> None:
        """Export the generated schedule to a JSON file."""
        if not self.schedule:
            print("No schedule to export.")
            return

        export_data = [
            {
                "course_id": e.course.id,
                "course_name": e.course.name,
                "teacher": e.course.teacher_name,
                "day": e.time_slot.day,
                "start_time": e.time_slot.start_time,
                "end_time": e.time_slot.end_time,
                "room_id": e.room.id,
                "room_type": e.room.room_type,
            }
            for e in self.schedule
        ]

        try:
            with open(filename, "w") as f:
                json.dump(export_data, f, indent=2)
            print(f"Schedule exported to {filename}")
        except IOError as e:
            print(f"Error exporting schedule: {e}")


def main() -> None:
    """Main entry point for running the timetable scheduler."""
    print("Dynamic Timetable Scheduler")
    print("=" * 50)

    scheduler = TimetableScheduler()

    print(f"\nLoaded {len(scheduler.courses)} courses")
    print(f"Loaded {len(scheduler.time_slots)} time slots")
    print(f"Loaded {len(scheduler.rooms)} rooms")

    print("\nGenerating timetable...")
    if scheduler.generate_schedule():
        print("✓ Timetable generated successfully!")
        scheduler.display_schedule()
        scheduler.display_schedule_by_day()

        conflicts = scheduler.check_conflicts()
        if conflicts:
            print(f"\n⚠️ Found {len(conflicts)} conflicts:")
            for conflict in conflicts:
                print(f"  - {conflict}")
        else:
            print("\n✓ No conflicts detected!")

        stats = scheduler.get_statistics()
        print("\nScheduling Statistics:")
        print(f"  Courses scheduled: {stats['scheduled_courses']}/{stats['total_courses']}")
        print(f"  Rooms utilized: {stats['used_rooms']}/{stats['total_rooms']}")
        print(f"  Time slots used: {stats['used_time_slots']}/{stats['total_time_slots']}")

        scheduler.export_schedule()
    else:
        print("❌ Failed to generate timetable. Check constraints and data.")


if __name__ == "__main__":
    main()
