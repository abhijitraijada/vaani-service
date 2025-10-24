from datetime import datetime, date
from typing import List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from fastapi import HTTPException, status

from app.models.event import Event
from app.models.registration import Registration
from app.models.registration_member import RegistrationMember
from app.models.daily_preference import DailyPreference
from app.models.event_day import EventDay
from app.models.host_assignment import HostAssignment
from app.models.host import Host
from app.schemas.dashboard import (
    EventDashboardResponse, RegistrationGroupInfo, RegistrationMemberInfo,
    DailyPreferenceInfo, DailyScheduleItem, DashboardSummary, ParticipantWithPreferences
)
from app.schemas.enums import RegistrationStatus, RegistrationType, TransportationMode, Gender, ToiletPreference


class DashboardService:
    """Service class for dashboard-related operations"""
    
    @staticmethod
    def get_event_dashboard(db: Session, event_id: str) -> EventDashboardResponse:
        """Get comprehensive dashboard data for an event using single optimized query"""
        try:
            # Single optimized query to get all data at once
            query = db.query(
                Event,
                EventDay,
                Registration,
                RegistrationMember,
                DailyPreference,
                HostAssignment,
                Host
            )\
            .outerjoin(EventDay, Event.id == EventDay.event_id)\
            .outerjoin(Registration, Event.id == Registration.event_id)\
            .outerjoin(RegistrationMember, Registration.id == RegistrationMember.registration_id)\
            .outerjoin(DailyPreference, Registration.id == DailyPreference.registration_id)\
            .outerjoin(HostAssignment, and_(
                RegistrationMember.id == HostAssignment.registration_member_id,
                EventDay.id == HostAssignment.event_day_id
            ))\
            .outerjoin(Host, HostAssignment.host_id == Host.id)\
            .filter(Event.id == event_id)\
            .order_by(EventDay.event_date, Registration.id, RegistrationMember.id)
            
            results = query.all()
            
            if not results:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Event not found"
                )
            
            # Extract event data (same for all rows)
            event = results[0][0]
            
            # Process all data from single query
            event_days_dict = {}
            registrations_dict = {}
            members_dict = {}
            preferences_dict = {}
            host_assignments_dict = {}
            
            for row in results:
                event_obj, event_day, registration, member, preference, host_assignment, host = row
                
                # Collect event days
                if event_day and event_day.id not in event_days_dict:
                    event_days_dict[event_day.id] = event_day
                
                # Collect registrations
                if registration and registration.id not in registrations_dict:
                    registrations_dict[registration.id] = {
                        'registration': registration,
                        'members': [],
                        'preferences': []
                    }
                
                # Collect members
                if member and member.id not in members_dict:
                    members_dict[member.id] = member
                    if registration:
                        registrations_dict[registration.id]['members'].append(member)
                
                # Collect preferences
                if preference and preference.id not in preferences_dict:
                    preferences_dict[preference.id] = preference
                    if registration:
                        registrations_dict[registration.id]['preferences'].append(preference)
                
                # Collect host assignments
                if host_assignment and host_assignment.id not in host_assignments_dict:
                    host_assignments_dict[host_assignment.id] = {
                        'assignment': host_assignment,
                        'host': host
                    }
            
            # Create mapping for host assignments by member_id and event_day_id
            member_host_mapping = {}
            for assignment_data in host_assignments_dict.values():
                assignment = assignment_data['assignment']
                host = assignment_data['host']
                key = f"{assignment.registration_member_id}_{assignment.event_day_id}"
                member_host_mapping[key] = host
            
            # Count participants for statistics
            total_participants = 0
            confirmed_participants = 0
            waiting_participants = 0
            
            for reg_data in registrations_dict.values():
                members = reg_data['members']
                
                for member in members:
                    total_participants += 1
                    if member.status == RegistrationStatus.CONFIRMED:
                        confirmed_participants += 1
                    elif member.status == RegistrationStatus.WAITING:
                        waiting_participants += 1
            
            # Create daily schedule with participants
            daily_schedule = []
            for event_day in sorted(event_days_dict.values(), key=lambda x: x.event_date or date.min):
                # Find all participants for this day
                day_participants = []
                
                for reg_data in registrations_dict.values():
                    registration = reg_data['registration']
                    members = reg_data['members']
                    preferences = reg_data['preferences']
                    
                    # Find preferences for this event day
                    day_preferences = [p for p in preferences if p.event_day_id == event_day.id]
                    
                    # Create participant objects for this day
                    for member in members:
                        # Find preference for this member and day
                        member_preference = None
                        for pref in day_preferences:
                            # Match preference to member (assuming one preference per member per day)
                            member_preference = pref
                            break
                        
                        # Find host assignment for this member and event day using efficient mapping
                        member_host_key = f"{member.id}_{event_day.id}"
                        member_host = member_host_mapping.get(member_host_key)
                        
                        # Create participant with all details
                        participant = ParticipantWithPreferences(
                            # Member details
                            id=member.id,
                            name=member.name,
                            phone_number=member.phone_number,
                            email=member.email,
                            city=member.city,
                            age=member.age,
                            gender=member.gender,
                            language=member.language,
                            floor_preference=member.floor_preference,
                            special_requirements=member.special_requirements,
                            status=member.status,
                            created_at=member.created_at,
                            updated_at=member.updated_at,
                            
                            # Daily preference details
                            staying_with_yatra=member_preference.staying_with_yatra if member_preference else True,
                            dinner_at_host=member_preference.dinner_at_host if member_preference else True,
                            breakfast_at_host=member_preference.breakfast_at_host if member_preference else True,
                            lunch_with_yatra=member_preference.lunch_with_yatra if member_preference else True,
                            physical_limitations=member_preference.physical_limitations if member_preference else None,
                            toilet_preference=member_preference.toilet_preference if member_preference else ToiletPreference.INDIAN,
                            
                            # Group/Registration details
                            group_id=registration.id,
                            registration_type=registration.registration_type,
                            transportation_mode=registration.transportation_mode,
                            has_empty_seats=registration.has_empty_seats,
                            available_seats_count=registration.available_seats_count,
                            notes=registration.notes,
                            
                            # Host assignment details (if assigned)
                            host_id=member_host.id if member_host else None,
                            host_name=member_host.name if member_host else None,
                            host_place_name=member_host.place_name if member_host else None,
                            host_phone_no=member_host.phone_no if member_host else None
                        )
                        day_participants.append(participant)
                
                # Calculate toilet preferences for this day - only from fully attending groups
                daily_toilet_preferences = {"indian": 0, "western": 0}
                
                # Group participants by group_id to check if all members are attending
                day_group_participants = {}
                for participant in day_participants:
                    group_id = participant.group_id
                    if group_id not in day_group_participants:
                        day_group_participants[group_id] = []
                    day_group_participants[group_id].append(participant)
                
                # Only count toilet preferences from groups where ALL members are confirmed/registered
                for group_id, group_participants in day_group_participants.items():
                    # Check if ALL participants in this group are either confirmed or registered
                    all_attending = all(
                        p.status.value in ['confirmed', 'registered'] 
                        for p in group_participants
                    )
                    
                    # Only count toilet preferences from fully attending groups
                    if all_attending:
                        for participant in group_participants:
                            if participant.toilet_preference:
                                toilet_pref = participant.toilet_preference.value
                                if toilet_pref in daily_toilet_preferences:
                                    daily_toilet_preferences[toilet_pref] += 1
                
                schedule_item = DailyScheduleItem(
                    event_day_id=event_day.id,
                    event_date=event_day.event_date,
                    location_name=event_day.location_name,
                    breakfast_provided=event_day.breakfast_provided,
                    lunch_provided=event_day.lunch_provided,
                    dinner_provided=event_day.dinner_provided,
                    daily_notes=event_day.daily_notes,
                    participants=day_participants,
                    toilet_preferences=daily_toilet_preferences
                )
                daily_schedule.append(schedule_item)
            
            # Generate summary statistics from daily schedule participants
            summary = DashboardService._generate_summary_from_participants(daily_schedule)
            
            return EventDashboardResponse(
                event_id=event_id,
                event_name=event.event_name,
                event_start_date=event.start_date,
                event_end_date=event.end_date,
                total_registrations=len(registrations_dict),
                total_participants=total_participants,
                confirmed_participants=confirmed_participants,
                waiting_participants=waiting_participants,
                daily_schedule=daily_schedule,
                summary=summary
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate dashboard: {str(e)}"
            )
    
    @staticmethod
    def _generate_summary_from_participants(daily_schedule: List[DailyScheduleItem]) -> Dict[str, Any]:
        """Generate summary statistics from daily schedule participants"""
        # Collect all unique participants across all days
        all_participants = []
        seen_participants = set()
        
        for day in daily_schedule:
            for participant in day.participants:
                if participant.id not in seen_participants:
                    all_participants.append(participant)
                    seen_participants.add(participant.id)
        
        # Count registration types and transportation modes - only from fully attending groups
        registration_types = {}
        transportation_modes = {}
        
        # Group participants by group_id first
        group_participants = {}
        for participant in all_participants:
            group_id = participant.group_id
            if group_id not in group_participants:
                group_participants[group_id] = []
            group_participants[group_id].append(participant)
        
        # Only count from groups where ALL members are confirmed/registered
        for group_id, participants in group_participants.items():
            # Check if ALL participants in this group are either confirmed or registered
            all_attending = all(
                p.status.value in ['confirmed', 'registered'] 
                for p in participants
            )
            
            # Only count statistics from fully attending groups
            if all_attending:
                for participant in participants:
                    # Count registration types
                    reg_type = participant.registration_type.value
                    registration_types[reg_type] = registration_types.get(reg_type, 0) + 1
                    
                    # Count transportation modes
                    transport = participant.transportation_mode.value
                    transportation_modes[transport] = transportation_modes.get(transport, 0) + 1
        
        # Count empty seats for unique groups with confirmed/registered participants
        groups_with_empty_seats = 0
        total_empty_seats = 0
        seen_groups = set()
        
        # Check each group for empty seats eligibility
        for group_id, participants in group_participants.items():
            if group_id not in seen_groups:
                seen_groups.add(group_id)
                
                # Check if ALL participants are either confirmed or registered
                all_attending = all(
                    p.status.value in ['confirmed', 'registered'] 
                    for p in participants
                )
                
                # Only count empty seats if ALL participants are attending and group has empty seats
                if all_attending and participants[0].has_empty_seats:
                    groups_with_empty_seats += 1
                    total_empty_seats += participants[0].available_seats_count or 0
        
        # Gender distribution, age groups, city distribution, and toilet preferences - only from fully attending groups
        gender_distribution = {"M": 0, "F": 0}
        age_groups = {"0-18": 0, "19-30": 0, "31-50": 0, "51+": 0}
        city_distribution = {}
        toilet_preferences = {"indian": 0, "western": 0}
        
        # Only count participants from groups where ALL members are confirmed/registered
        for group_id, participants in group_participants.items():
            # Check if ALL participants in this group are either confirmed or registered
            all_attending = all(
                p.status.value in ['confirmed', 'registered'] 
                for p in participants
            )
            
            # Only count statistics from fully attending groups
            if all_attending:
                for participant in participants:
                    # Gender distribution
                    if participant.gender in gender_distribution:
                        gender_distribution[participant.gender] += 1
                    
                    # Age groups
                    if participant.age:
                        if participant.age <= 18:
                            age_groups["0-18"] += 1
                        elif participant.age <= 30:
                            age_groups["19-30"] += 1
                        elif participant.age <= 50:
                            age_groups["31-50"] += 1
                        else:
                            age_groups["51+"] += 1
                    
                    # City distribution
                    if participant.city:
                        city_distribution[participant.city] = city_distribution.get(participant.city, 0) + 1
                    
                    # Toilet preferences
                    if participant.toilet_preference:
                        toilet_pref = participant.toilet_preference.value
                        if toilet_pref in toilet_preferences:
                            toilet_preferences[toilet_pref] += 1
        
        # Calculate daily toilet preferences for summary
        daily_toilet_preferences = {}
        for day in daily_schedule:
            day_key = day.event_date.isoformat() if day.event_date else day.event_day_id
            daily_toilet_preferences[day_key] = day.toilet_preferences

        return {
            "total_groups": len(set(p.group_id for p in all_participants)),
            "individual_registrations": registration_types.get("individual", 0),
            "group_registrations": registration_types.get("group", 0),
            "public_transport": transportation_modes.get("public", 0),
            "private_transport": transportation_modes.get("private", 0),
            "groups_with_empty_seats": groups_with_empty_seats,
            "total_empty_seats": total_empty_seats,
            "gender_distribution": gender_distribution,
            "age_groups": age_groups,
            "city_distribution": city_distribution,
            "toilet_preferences": toilet_preferences,
            "daily_toilet_preferences": daily_toilet_preferences
        }
