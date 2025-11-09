
#========================================================#
# this script provides database services and queries for the HandyChat application
# It interacts with the SQLAlchemy models to retrieve information about sports classes, schedules, locations, and teachers
#========================================================#


from extensions import db
from models import SportClass, ClassSchedule, Location, Teacher
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        pass
    
    def find_class_info(self, sport_name, time_reference="today"):
        """Enhanced class info finder using database"""
        try:
            sport_class = SportClass.query.filter(
                SportClass.name.ilike(f'%{sport_name}%')
            ).first()
            
            if not sport_class:
                logger.warning(f"Sport class not found: {sport_name}")
                return None
            
            # Get schedule
            schedule = ClassSchedule.query.filter_by(
                class_id=sport_class.id, 
                is_active=True
            ).first()
            
            # Get location and teacher
            location = Location.query.get(sport_class.location_id)
            teacher = Teacher.query.get(sport_class.teacher_id)
            
            return {
                'sport_name': sport_class.name,
                'description': sport_class.description,
                'location_name': location.name,
                'building': location.building,
                'floor': location.floor,
                'room_number': location.room_number,
                'location_description': location.description,
                'schedule_day': schedule.day_of_week if schedule else None,
                'schedule_time': f"{schedule.start_time} - {schedule.end_time}" if schedule else None,
                'teacher_name': teacher.name if teacher else None,
                'teacher_contact': teacher.contact_info if teacher else None,
                'teacher_email': teacher.email if teacher else None,
                'images': location.image_urls if hasattr(location, 'image_urls') else []
            }
            
        except Exception as e:
            logger.error(f"Error finding class info: {e}")
            return None
    
    def get_available_sports(self):
        """Get available sports from database"""
        try:
            sports = SportClass.query.with_entities(SportClass.name).distinct().all()
            return [sport[0] for sport in sports] if sports else []
        except Exception as e:
            logger.error(f"Error getting available sports: {e}")
            return ["basketball", "swimming", "tennis", "badminton", "soccer", "volleyball", "table tennis", "tai chi"]
    
    def get_class_schedule(self, sport_name):
        """Get detailed schedule for a sport"""
        try:
            sport_class = SportClass.query.filter(
                SportClass.name.ilike(f'%{sport_name}%')
            ).first()
            
            if not sport_class:
                return []
            
            schedules = ClassSchedule.query.filter_by(
                class_id=sport_class.id, 
                is_active=True
            ).all()
            
            return [
                {
                    'day': schedule.day_of_week,
                    'time': f"{schedule.start_time} - {schedule.end_time}",
                    'semester': schedule.semester
                }
                for schedule in schedules
            ]
            
        except Exception as e:
            logger.error(f"Error getting class schedule: {e}")
            return []
    
    def search_classes_by_teacher(self, teacher_name):
        """Search classes by teacher name"""
        try:
            teacher = Teacher.query.filter(
                Teacher.name.ilike(f'%{teacher_name}%')
            ).first()
            
            if not teacher:
                return []
            
            classes = SportClass.query.filter_by(teacher_id=teacher.id).all()
            return [
                {
                    'sport_name': sport_class.name,
                    'schedule': self.get_class_schedule(sport_class.name)
                }
                for sport_class in classes
            ]
            
        except Exception as e:
            logger.error(f"Error searching classes by teacher: {e}")
            return []

# Global instance
database_service = DatabaseService()