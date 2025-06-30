% Dynamic Timetable Scheduler - Prolog Logic
% File: timetable_scheduler.pl

% --- Facts ---

% course(CourseID, CourseName, TeacherID, DurationInHours, RequiredRoomType)
course(cs101, 'Computer Science 101', t001, 2, computer_lab).
course(cs102, 'Data Structures', t002, 2, computer_lab).
course(math101, 'Calculus I', t003, 1, classroom).
course(math102, 'Linear Algebra', t004, 2, classroom).
course(phy101, 'Physics I', t005, 2, physics_lab).
course(eng101, 'English Literature', t006, 1, classroom).
course(chem101, 'Chemistry I', t007, 2, chemistry_lab).
course(hist101, 'World History', t008, 1, classroom).
course(bio101, 'Biology I', t009, 2, biology_lab).
course(stat101, 'Statistics', t010, 1, classroom).

% teacher(TeacherID, TeacherName, Department)
teacher(t001, 'Dr. Smith', computer_science).
teacher(t002, 'Prof. Johnson', computer_science).
teacher(t003, 'Dr. Brown', mathematics).
teacher(t004, 'Prof. Davis', mathematics).
teacher(t005, 'Dr. Wilson', physics).
teacher(t006, 'Prof. Miller', english).
teacher(t007, 'Dr. Garcia', chemistry).
teacher(t008, 'Prof. Martinez', history).
teacher(t009, 'Dr. Anderson', biology).
teacher(t010, 'Prof. Taylor', statistics).

% room(RoomID, RoomType, Capacity)
room(r001, computer_lab, 30).
room(r002, computer_lab, 25).
room(r003, classroom, 40).
room(r004, classroom, 35).
room(r005, classroom, 50).
room(r006, physics_lab, 20).
room(r007, chemistry_lab, 25).
room(r008, biology_lab, 30).
room(r009, classroom, 45).
room(r010, classroom, 40).

% time_slot(SlotID, Day, StartTime, EndTime, DurationInHours)
time_slot(slot1, monday, 800, 900, 1).
time_slot(slot2, monday, 900, 1000, 1).
time_slot(slot3, monday, 1000, 1200, 2).
time_slot(slot4, monday, 1300, 1400, 1).
time_slot(slot5, monday, 1400, 1600, 2).

time_slot(slot6, tuesday, 800, 900, 1).
time_slot(slot7, tuesday, 900, 1000, 1).
time_slot(slot8, tuesday, 1000, 1200, 2).
time_slot(slot9, tuesday, 1300, 1400, 1).
time_slot(slot10, tuesday, 1400, 1600, 2).

time_slot(slot11, wednesday, 800, 900, 1).
time_slot(slot12, wednesday, 900, 1000, 1).
time_slot(slot13, wednesday, 1000, 1200, 2).
time_slot(slot14, wednesday, 1300, 1400, 1).
time_slot(slot15, wednesday, 1400, 1600, 2).

time_slot(slot16, thursday, 800, 900, 1).
time_slot(slot17, thursday, 900, 1000, 1).
time_slot(slot18, thursday, 1000, 1200, 2).
time_slot(slot19, thursday, 1300, 1400, 1).
time_slot(slot20, thursday, 1400, 1600, 2).

time_slot(slot21, friday, 800, 900, 1).
time_slot(slot22, friday, 900, 1000, 1).
time_slot(slot23, friday, 1000, 1200, 2).
time_slot(slot24, friday, 1300, 1400, 1).
time_slot(slot25, friday, 1400, 1600, 2).

% --- Dynamic predicate to store the current schedule ---
:- dynamic(schedule/3).

% --- Rules ---

% suitable_room(+CourseID, +RoomID)
% True if the room matches the course's required room type
suitable_room(CourseID, RoomID) :-
    course(CourseID, _, _, _, RequiredRoomType),
    room(RoomID, RoomType, _),
    (RequiredRoomType = RoomType ; RequiredRoomType = any).

% suitable_time(+CourseID, +SlotID)
% True if the time slot duration is enough for the course duration
suitable_time(CourseID, SlotID) :-
    course(CourseID, _, _, Duration, _),
    time_slot(SlotID, _, _, _, SlotDuration),
    Duration =< SlotDuration.

% teacher_available(+TeacherID, +SlotID)
% True if the teacher is free in the given time slot (no conflicting course)
teacher_available(TeacherID, SlotID) :-
    \+ (schedule(OtherCourse, SlotID, _),
        course(OtherCourse, _, TeacherID, _, _)).

% room_available(+RoomID, +SlotID)
% True if the room is free in the given time slot
room_available(RoomID, SlotID) :-
    \+ schedule(_, SlotID, RoomID).

% valid_assignment(+CourseID, +SlotID, +RoomID)
% True if assigning the course to the time slot and room is valid
valid_assignment(CourseID, SlotID, RoomID) :-
    course(CourseID, _, TeacherID, _, _),
    suitable_room(CourseID, RoomID),
    suitable_time(CourseID, SlotID),
    teacher_available(TeacherID, SlotID),
    room_available(RoomID, SlotID).

% assign_course(+CourseID, +SlotID, +RoomID)
% Assigns the course to a valid slot and room
assign_course(CourseID, SlotID, RoomID) :-
    valid_assignment(CourseID, SlotID, RoomID),
    assertz(schedule(CourseID, SlotID, RoomID)).

% generate_timetable
% Clears existing schedule and assigns all courses arbitrarily
generate_timetable :-
    retractall(schedule(_, _, _)),
    findall(CourseID, course(CourseID, _, _, _, _), Courses),
    assign_all_courses(Courses).

% assign_all_courses(+Courses)
% Assigns each course from the list to some valid slot and room
assign_all_courses([]).
assign_all_courses([CourseID|Rest]) :-
    assign_course(CourseID, _, _),
    assign_all_courses(Rest).

% find_assignment(+CourseID, -SlotID, -RoomID)
% Finds any valid assignment for the given course
find_assignment(CourseID, SlotID, RoomID) :-
    valid_assignment(CourseID, SlotID, RoomID).

% get_all_assignments(+CourseID, -Assignments)
% Gets all possible assignments [SlotID, RoomID] for the course
get_all_assignments(CourseID, Assignments) :-
    findall([SlotID, RoomID],
            find_assignment(CourseID, SlotID, RoomID),
            Assignments).

% get_schedule(-Schedule)
% Retrieves the current schedule as a list of [CourseID, SlotID, RoomID]
get_schedule(Schedule) :-
    findall([CourseID, SlotID, RoomID],
            schedule(CourseID, SlotID, RoomID),
            Schedule).

% schedule_complete
% True if all courses are scheduled
schedule_complete :-
    findall(CourseID, course(CourseID, _, _, _, _), AllCourses),
    findall(CourseID, schedule(CourseID, _, _), ScheduledCourses),
    sort(AllCourses, SortedAll),
    sort(ScheduledCourses, SortedScheduled),
    SortedAll = SortedScheduled.

% get_course_details(+CourseID, -CourseName, -TeacherName, -Duration, -RoomType)
get_course_details(CourseID, CourseName, TeacherName, Duration, RoomType) :-
    course(CourseID, CourseName, TeacherID, Duration, RoomType),
    teacher(TeacherID, TeacherName, _).

% get_time_details(+SlotID, -Day, -StartTime, -EndTime)
get_time_details(SlotID, Day, StartTime, EndTime) :-
    time_slot(SlotID, Day, StartTime, EndTime, _).

% get_room_details(+RoomID, -RoomType, -Capacity)
get_room_details(RoomID, RoomType, Capacity) :-
    room(RoomID, RoomType, Capacity).

% clear_schedule
% Clears all scheduled assignments
clear_schedule :-
    retractall(schedule(_, _, _)).

% generate_optimal_timetable
% Generates an optimal timetable using backtracking, preferring earlier slots
generate_optimal_timetable :-
    clear_schedule,
    findall(CourseID, course(CourseID, _, _, _, _), Courses),
    assign_courses_optimally(Courses).

% assign_courses_optimally(+Courses)
% Assign courses one by one with best assignments
assign_courses_optimally([]).
assign_courses_optimally([CourseID|Rest]) :-
    find_best_assignment(CourseID, SlotID, RoomID),
    assertz(schedule(CourseID, SlotID, RoomID)),
    assign_courses_optimally(Rest).

% find_best_assignment(+CourseID, -BestSlot, -BestRoom)
% Finds the best assignment (earliest slot) for a course
find_best_assignment(CourseID, BestSlot, BestRoom) :-
    findall([SlotID, RoomID],
            valid_assignment(CourseID, SlotID, RoomID),
            Assignments),
    Assignments \= [],
    sort_assignments_by_preference(Assignments, [ [BestSlot, BestRoom] | _ ]).

% sort_assignments_by_preference(+Assignments, -SortedAssignments)
% Sort assignments by SlotID ascending (assuming slot IDs can be ordered)
sort_assignments_by_preference(Assignments, SortedAssignments) :-
    sort(Assignments, SortedAssignments).

% get_timetable_by_day(+Day, -DaySchedule)
% Gets the schedule for a specific day as list of [CourseID, SlotID, RoomID]
get_timetable_by_day(Day, DaySchedule) :-
    findall([CourseID, SlotID, RoomID],
            (schedule(CourseID, SlotID, RoomID),
             time_slot(SlotID, Day, _, _, _)),
            DaySchedule).

% get_teacher_schedule(+TeacherID, -TeacherSchedule)
% Gets schedule for a specific teacher
get_teacher_schedule(TeacherID, TeacherSchedule) :-
    findall([CourseID, SlotID, RoomID],
            (schedule(CourseID, SlotID, RoomID),
             course(CourseID, _, TeacherID, _, _)),
            TeacherSchedule).
