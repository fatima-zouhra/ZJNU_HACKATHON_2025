from app import create_app
from models import db, Location, Teacher, SportClass, ClassSchedule
from datetime import datetime

def create_sample_data():
    app = create_app()

    with app.app_context():
        # Clear existing data
        try:
            db.session.query(ClassSchedule).delete()
            db.session.query(SportClass).delete()
            db.session.query(Teacher).delete()
            db.session.query(Location).delete()
            db.session.commit()
            print("Cleared existing data")
        except Exception as e:
            print(f"❌ Clear data error: {e}")
            db.session.rollback()
        
        current_time = datetime.utcnow()
        
        gym_location = Location(
            name="North Gymnasium",
            building="Sports Complex A",
            floor="1st Floor",
            room_number="GYM-101",
            description="Basketball court with maple wood flooring, 4 hoops, and electronic scoreboard. Capacity: 500 spectators.",
            image_urls=[  
                "/static/images/basketball/basketballIndoor1.jpg",
                "/static/images/basketball/basketballIndoor3.jpg"
            ],
            latitude=39.9042,
            longitude=116.4074,
            amap_link="https://uri.amap.com/BJ001",
            baidu_map_link="https://map.baidu.com/dir/BJ001",
            created_at=current_time
        )
        
        pool_location = Location(
            name="Swimming Pool",
            building="Aquatics Center", 
            floor="Ground Floor",
            room_number="POOL-01",
            description="Olympic-sized swimming pool with 8 lanes, diving boards, and professional timing system.",
            image_urls=[
                "/static/images/swimmingPool/1.jpg",
                "/static/images/swimmingPool/2.jpg",
                "/static/images/swimmingPool/3.jpg",
            ],
            latitude=39.9045,
            longitude=116.4078,
            amap_link="https://uri.amap.com/BJ002",
            baidu_map_link="https://map.baidu.com/dir/BJ002",
            created_at=current_time
        )
        
        tennis_location = Location(
            name="Tennis Complex",
            building="Outdoor Sports Facility",
            floor="Outdoor",
            room_number="TC-1-4",
            description="Four professional hard courts with night lighting and spectator seating. Court reservation system available.",
            image_urls=[
                "/static/images/tennisCourt/1.jpg",
                "/static/images/tennisCourt/5.jpg",
                "/static/images/tennisCourt/6.jpg"
            ],
            latitude=39.9038,
            longitude=116.4082,
            amap_link="https://uri.amap.com/BJ003",
            baidu_map_link="https://map.baidu.com/dir/BJ003",
            created_at=current_time
        )
        
        badminton_location = Location(
            name="Badminton Hall",
            building="Indoor Sports Center",
            floor="1st Floor",
            room_number="BH-201",
            description="9 professional badminton courts with sprung flooring, international standard lighting, and equipment rental.",
            image_urls=[
                "/static/images/badminton/1.jpg",
                "/static/images/badminton/2.jpg"
            ],
            latitude=39.9040,
            longitude=116.4068,
            amap_link="https://uri.amap.com/BJ004",
            baidu_map_link="https://map.baidu.com/dir/BJ004",
            created_at=current_time
        )
        
        soccer_location = Location(
            name="Soccer Stadium",
            building="Outdoor Sports Complex",
            floor="Field Level",
            room_number="STAD-01",
            description="Full-size professional soccer field with artificial turf, track surrounding, and seating for 1000 spectators.",
            image_urls=["/static/images/soccer/1.jpg"],
            latitude=39.9035,
            longitude=116.4090,
            amap_link="https://uri.amap.com/BJ005",
            baidu_map_link="https://map.baidu.com/dir/BJ005",
            created_at=current_time
        )
        
        volleyball_location = Location(
            name="Volleyball Arena",
            building="Sports Complex B",
            floor="1st Floor",
            room_number="VB-101",
            description="Indoor volleyball courts with professional net systems, sand court option, and training equipment.",
            image_urls=[
                "/static/images/volleyball/1.jpg",
                "/static/images/volleyball/2.jpg"
            ],
            latitude=39.9048,
            longitude=116.4070,
            amap_link="https://uri.amap.com/BJ006",
            baidu_map_link="https://map.baidu.com/dir/BJ006",
            created_at=current_time
        )
        
        table_tennis_location = Location(
            name="Table Tennis Hall",
            building="Indoor Sports Center",
            floor="3rd Floor",
            room_number="TT-301",
            description="12 professional table tennis tables with international standard flooring and lighting for competition.",
            image_urls=[
                "/static/images/tableTennis/1.jpg",
                "/static/images/tableTennis/2.jpg"
            ],
            latitude=39.9043,
            longitude=116.4065,
            amap_link="https://uri.amap.com/BJ007",
            baidu_map_link="https://map.baidu.com/dir/BJ007",
            created_at=current_time
        )
        
        tai_chi_location = Location(
            name="Tai Chi Garden",
            building="Traditional Arts Pavilion",
            floor="Ground Floor",
            room_number="TCG-001",
            description="Peaceful outdoor garden and indoor hall for Tai Chi practice. Features traditional architecture and serene environment.",
            image_urls=["/static/images/taiChi/1.jpg"],
            latitude=39.9052,
            longitude=116.4088,
            amap_link="https://uri.amap.com/BJ008",
            baidu_map_link="https://map.baidu.com/dir/BJ008",
            created_at=current_time
        )
        
        coach_zhang = Teacher(
            name="Coach Zhang Wei",
            created_at=current_time
        )
        
        coach_li = Teacher(
            name="Coach Li Ming", 
            created_at=current_time
        )
        
        coach_wang = Teacher(
            name="Coach Wang Fang",
            created_at=current_time
        )
        
        coach_chen = Teacher(
            name="Coach Chen Gang", 
            created_at=current_time
        )
        
        coach_yang = Teacher(
            name="Coach Yang Jing",
            created_at=current_time
        )
        
        coach_liu = Teacher(
            name="Coach Liu Mei",
            created_at=current_time
        )
        
        coach_zhao = Teacher(
            name="Coach Zhao Qiang",
            created_at=current_time
        )
        
        master_wu = Teacher(
            name="Master Wu Jian",
            created_at=current_time
        )
        
        # Add to session and commit
        try:
            db.session.add_all([
                gym_location, pool_location, tennis_location, badminton_location, 
                soccer_location, volleyball_location, table_tennis_location, tai_chi_location,
                coach_zhang, coach_li, coach_wang, coach_chen, coach_yang, coach_liu, coach_zhao, master_wu
            ])
            db.session.commit()
            print("Locations and teachers created successfully")
        except Exception as e:
            print(f"❌ Error creating locations/teachers: {e}")
            db.session.rollback()
            raise
        
        try:
            basketball = SportClass(
                name="basketball",
                description="Basketball PE Class - Learn fundamental skills, team strategies, and game techniques",
                location_id=gym_location.id,
                teacher_id=coach_zhang.id,
                created_at=current_time
            )
            
            swimming = SportClass(
                name="swimming", 
                description="Swimming PE Class - Basic strokes, water safety, and endurance training",
                location_id=pool_location.id,
                teacher_id=coach_li.id,
                created_at=current_time
            )
            
            tennis = SportClass(
                name="tennis",
                description="Tennis PE Class - Forehand, backhand, serving, and match play", 
                location_id=tennis_location.id,
                teacher_id=coach_wang.id,
                created_at=current_time
            )
            
            badminton = SportClass(
                name="badminton",
                description="Badminton PE Class - Footwork, smashing techniques, and doubles strategy",
                location_id=badminton_location.id,
                teacher_id=coach_chen.id,
                created_at=current_time
            )
            
            soccer = SportClass(
                name="soccer",
                description="Soccer PE Class - Dribbling, passing, shooting, and team formation",
                location_id=soccer_location.id,
                teacher_id=coach_yang.id,
                created_at=current_time
            )
            
            volleyball = SportClass(
                name="volleyball",
                description="Volleyball PE Class - Serving, spiking, blocking, and team coordination",
                location_id=volleyball_location.id,
                teacher_id=coach_liu.id,
                created_at=current_time
            )
            
            table_tennis = SportClass(
                name="table tennis",
                description="Table Tennis PE Class - Basic strokes, spin techniques, and match strategy",
                location_id=table_tennis_location.id,
                teacher_id=coach_zhao.id,
                created_at=current_time
            )
            
            tai_chi = SportClass(
                name="tai chi",
                description="Tai Chi PE Class - Learn traditional Tai Chi movements, breathing techniques, and meditation for health and balance",
                location_id=tai_chi_location.id,
                teacher_id=master_wu.id,
                created_at=current_time
            )
            
            db.session.add_all([basketball, swimming, tennis, badminton, soccer, volleyball, table_tennis, tai_chi])
            db.session.commit()
            print("Sport classes created successfully")
        except Exception as e:
            print(f"❌ Error creating sport classes: {e}")
            db.session.rollback()
            raise
        
        try:
            schedules = [
                
                ClassSchedule(class_id=basketball.id, day_of_week="Monday", start_time="08:00", end_time="09:20", semester="Fall 2025", is_active=True, created_at=current_time),
                ClassSchedule(class_id=basketball.id, day_of_week="Wednesday", start_time="14:00", end_time="15:20", semester="Fall 2025", is_active=True, created_at=current_time),
                
                ClassSchedule(class_id=swimming.id, day_of_week="Tuesday", start_time="10:00", end_time="11:20", semester="Fall 2025", is_active=True, created_at=current_time),
                ClassSchedule(class_id=swimming.id, day_of_week="Thursday", start_time="10:00", end_time="11:20", semester="Fall 2025", is_active=True, created_at=current_time),
                
                ClassSchedule(class_id=tennis.id, day_of_week="Monday", start_time="14:00", end_time="15:20", semester="Fall 2025", is_active=True, created_at=current_time),
                ClassSchedule(class_id=tennis.id, day_of_week="Friday", start_time="14:00", end_time="15:20", semester="Fall 2025", is_active=True, created_at=current_time),
                
                ClassSchedule(class_id=badminton.id, day_of_week="Tuesday", start_time="18:00", end_time="19:20", semester="Fall 2025", is_active=True, created_at=current_time),
                ClassSchedule(class_id=badminton.id, day_of_week="Friday", start_time="15:00", end_time="16:20", semester="Fall 2025", is_active=True, created_at=current_time),
                
                ClassSchedule(class_id=soccer.id, day_of_week="Wednesday", start_time="10:00", end_time="11:20", semester="Fall 2025", is_active=True, created_at=current_time),
                ClassSchedule(class_id=soccer.id, day_of_week="Thursday", start_time="14:00", end_time="15:20", semester="Fall 2025", is_active=True, created_at=current_time),
                
                ClassSchedule(class_id=volleyball.id, day_of_week="Monday", start_time="08:40", end_time="10:00", semester="Fall 2025", is_active=True, created_at=current_time),
                ClassSchedule(class_id=volleyball.id, day_of_week="Wednesday", start_time="09:00", end_time="10:20", semester="Fall 2025", is_active=True, created_at=current_time),
                
                ClassSchedule(class_id=table_tennis.id, day_of_week="Tuesday", start_time="09:40", end_time="11:00", semester="Fall 2025", is_active=True, created_at=current_time),
                ClassSchedule(class_id=table_tennis.id, day_of_week="Thursday", start_time="15:40", end_time="17:00", semester="Fall 2025", is_active=True, created_at=current_time),
                

                ClassSchedule(class_id=tai_chi.id, day_of_week="Monday", start_time="14:00", end_time="15:20", semester="Fall 2025", is_active=True, created_at=current_time),
                ClassSchedule(class_id=tai_chi.id, day_of_week="Wednesday", start_time="08:00", end_time="09:20", semester="Fall 2025", is_active=True, created_at=current_time),
                ClassSchedule(class_id=tai_chi.id, day_of_week="Friday", start_time="08:00", end_time="09:20", semester="Fall 2025", is_active=True, created_at=current_time),
            ]
            
            db.session.add_all(schedules)
            db.session.commit()
            print("Class schedules created successfully")
        except Exception as e:
            print(f"❌ Error creating schedules: {e}")
            db.session.rollback()
            raise
        
        print("PE Sample data creation completed!")
        print("Final Summary:")
        print("   - 8 locations with multiple images")
        print("   - 8 teachers with contact information") 
        print("   - 8 sport classes")
        print("   - 17 class schedules")

def create_handbook_data():
    """Initialize handbook data in database"""
    app = create_app()
    with app.app_context():
        from services.handbook_db_service import handbook_db_service
        success = handbook_db_service.initialize_handbook_data()
        if success:
            print("Handbook data created successfully")
        else:
            print("❌ Failed to create handbook data")

# This allows the file to be run directly or imported
if __name__ == '__main__':
    create_sample_data()
    create_handbook_data()
    print("🎉 All sample data creation completed!")
