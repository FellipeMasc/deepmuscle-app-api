import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import col, delete, func, select
from api.auth.main import get_current_user
from rag_conversation.suggestions import generate_workout_suggestions
from sql.models import (
    DayExercises,
    Exercises,
    UserDetails,
    Users,
    WorkoutDays,
    Workouts,
)
from api.deps import SessionDep
from sql.schemas import UserDetailsCreate, UserOut
import datetime
from fastapi.responses import JSONResponse, Response
from rag_conversation.suggestions import generate_workout_suggestions
from sqlalchemy import and_

user_router = APIRouter(prefix="/users", tags=["users"])

days_dict ={
        1: "Segunda-feira",
        2: "Terça-feira",
        3: "Quarta-feira",
        4: "Quinta-feira",
        5: "Sexta-feira",
        6: "Sábado",
        7: "Domingo",
    }

def process_user_detail_in_llm(new_user_details: UserDetails, db: SessionDep):
    workout_suggestions = generate_workout_suggestions(new_user_details)
    
    if "error" in workout_suggestions:
        raise HTTPException(status_code=500, detail=workout_suggestions["error"])

    current_user_details = db.query(UserDetails).filter(UserDetails.id == new_user_details.id).first()
    
    # Store generated workout details in the database
    new_workout = Workouts(
        name=workout_suggestions["workout_name"],
        description=workout_suggestions["description"],
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)

    # Assign the workout ID to the user details
    current_user_details.workout_id = new_workout.id
    current_user_details.current_workout_day = 1
    db.commit()
    db.refresh(current_user_details)
    # Store workout days and exercises
    for day_data in workout_suggestions["days"]:
        workout_day = db.query(WorkoutDays).filter(and_(WorkoutDays.user_id == new_user_details.user_id, WorkoutDays.day == day_data["day"])).first()
        if not workout_day:
            new_workout_day = WorkoutDays(
                user_id=new_user_details.user_id,
                day=day_data["day"],
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
            )
            db.add(new_workout_day)
            db.commit()
            db.refresh(new_workout_day)
            workout_day_id = new_workout_day.id
        else:
            workout_day_id = workout_day.id
            db.query(DayExercises).filter(DayExercises.workout_day_id == workout_day_id).delete()
        # Add exercises for each workout day
        for exercise_data in day_data["exercises"]:
            # Check if the exercise already exists
            existing_exercise = (
                db.query(Exercises)
                .filter(Exercises.name == exercise_data["name"])
                .first()
            )
            if not existing_exercise:
                new_exercise = Exercises(
                    name=exercise_data["name"],
                    category=exercise_data["category"],
                    description=exercise_data["description"],
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now(),
                )
                db.add(new_exercise)
                db.commit()
                db.refresh(new_exercise)
                exercise_id = new_exercise.id
            else:
                exercise_id = existing_exercise.id

            new_day_exercise = DayExercises(
                workout_day_id=new_workout_day.id,
                exercise_id=exercise_id,
                series = exercise_data["series"],
                repetitions = exercise_data["reps"],
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
            )
            db.add(new_day_exercise)
            db.commit()
            db.refresh(new_day_exercise)
    print("Workout details stored successfully")

@user_router.post("/register_details")
async def register_details(
    form_data: UserDetailsCreate,
    db: SessionDep,
    background_tasks: BackgroundTasks,
    user: UserOut = Depends(get_current_user),
):
    db_user = db.query(Users).filter(Users.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User does not exist")

    current = db.query(UserDetails).filter(UserDetails.user_id == db_user.id).first()
    if current:
        #change parameters
        current.age = form_data.age
        current.height = form_data.height
        current.weight = form_data.weight
        current.fitness_level = form_data.fitness_level
        current.gender = form_data.gender
        current.updated_at = datetime.datetime.now()
        db.commit()
        db.refresh(current)
        background_tasks.add_task(process_user_detail_in_llm, current, db)
        return Response(status_code=201, content="User details updated successfully")
        
        
    
    # Create and store user details
    new_user_details = UserDetails(
        user_id=db_user.id,
        age=form_data.age,
        height=form_data.height,
        weight=form_data.weight,
        gender=form_data.gender,
        fitness_level=form_data.fitness_level,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )

    db.add(new_user_details)
    db.commit()
    db.refresh(new_user_details)
    
    background_tasks.add_task(process_user_detail_in_llm, new_user_details, db)
    return Response(status_code=201, content="User details registered successfully")



@user_router.get("/check_workout_day")
async def check_workout_day(db: SessionDep, user: UserOut = Depends(get_current_user)):
    db_user = db.query(Users).filter(Users.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="User does not exist")

    user_details = (
        db.query(UserDetails).filter(UserDetails.user_id == db_user.id).first()
    )

    workout_day = (
        db.query(WorkoutDays)
        .filter(
            and_(
            WorkoutDays.user_id == db_user.id,
            WorkoutDays.day == user_details.current_workout_day)
        )
        .first()
        .day
    )
    if not workout_day:
        raise HTTPException(status_code=400, detail="User does not have a workout day")

    return Response(status_code=200, content="User has a workout day")


@user_router.post("/update_workout_day")
async def update_workout_day(
    db: SessionDep, user: UserOut = Depends(get_current_user)
):
    user_details = (
        db.query(UserDetails).filter(UserDetails.user_id == user.id).first()
    )

    next_day = (
        db.query(WorkoutDays)
        .filter(
            and_(
                WorkoutDays.user_id == user.id,
                WorkoutDays.day == days_dict[user_details.current_workout_day + 1] 
            )
        )
        .first()
    )

    if not next_day or not user_details.current_workout_day:
        user_details.current_workout_day = 1
    else:
        user_details.current_workout_day += 1

    db.commit()
    db.refresh(user_details)
    return Response(status_code=200, content="Dia de treino atualizado com sucesso")


@user_router.get("/get_day_exercises")
async def get_day_exercises(db: SessionDep, user: UserOut = Depends(get_current_user)):

    user_details = (
        db.query(UserDetails).filter(UserDetails.user_id == user.id).first()
    )
    workout_day = None
    if user_details and user_details.workout_id:
        if not user_details.current_workout_day:
            user_details.current_workout_day = 1
            db.commit()
            db.refresh(user_details)
        workout_day = (
            db.query(WorkoutDays)
            .filter(
                and_(WorkoutDays.user_id == user.id,
                WorkoutDays.day == days_dict[user_details.current_workout_day])
            )
            .first()
        )

    if not workout_day:
        raise HTTPException(status_code=400, detail="User does not have a workout day")
    
    exercises = (
        db.query(DayExercises)
        .filter(DayExercises.workout_day_id == workout_day.id)
        .all()
    )

    exercise_ids = [exercise.exercise_id for exercise in exercises]
    exercise_without_series_reps = db.query(Exercises).filter(Exercises.id.in_(exercise_ids)).all()

    exercise_list = []
    for exercise in exercise_without_series_reps:
            exercise_dict = {
                "name": exercise.name,
                "category": exercise.category,
                "description": exercise.description
            }
            exercise_dict["series"] = exercises[exercise_ids.index(exercise.id)].series
            exercise_dict["reps"] = exercises[exercise_ids.index(exercise.id)].repetitions
            exercise_list.append(exercise_dict)
    
    return exercise_list

@user_router.get("/get_all_user_exercises")
async def get_all_user_exercises(db: SessionDep, user: UserOut = Depends(get_current_user)):
    
    workout_day = (
        db.query(WorkoutDays)
        .filter(
            WorkoutDays.user_id == user.id
        )
        .all()
    )
    
    if not workout_day:
        raise HTTPException(status_code=400, detail="User does not have a workout day")
    
    exercises = {}
    for day in workout_day:
        exercises_day = (
            db.query(DayExercises)
            .filter(DayExercises.workout_day_id == day.id)
            .all()
        )
        
        exercise_ids_day = [exercise.exercise_id for exercise in exercises_day]
        
        exercise_without_series_reps = db.query(Exercises).filter(Exercises.id.in_(exercise_ids_day)).all()
        
        exercise_list = []
        for exercise in exercise_without_series_reps:
            exercise_dict = {
                "name": exercise.name,
                "category": exercise.category,
                "description": exercise.description
            }
            exercise_dict["series"] = exercises_day[exercise_ids_day.index(exercise.id)].series
            exercise_dict["reps"] = exercises_day[exercise_ids_day.index(exercise.id)].repetitions
            exercise_list.append(exercise_dict)
        
        exercises[day.day] = exercise_list

    
    return exercises
            
                  
@user_router.get("/get_user_infos")
async def get_user_infos(db: SessionDep, user: UserOut = Depends(get_current_user)):
    db_user = db.query(Users).filter(Users.email == user.email).first()
    user_details = db.query(UserDetails).filter(UserDetails.user_id == db_user.id).first()
    if not user_details:
        return{
            "full_name": db_user.full_name,
            "email": db_user.email,
            "age": None,
            "height": None,
            "weight": None,
            "exercise_level": None,
            "current_workout_day": None
        }
    
    return {
        "full_name": db_user.full_name,
        "email": db_user.email,
        "age": user_details.age,
        "height": user_details.height,
        "weight": user_details.weight,
        "gender": user_details.gender,
        "exercise_level": user_details.fitness_level,
        "current_workout_day": user_details.current_workout_day
    }

