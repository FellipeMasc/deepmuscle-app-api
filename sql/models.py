from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Identity, Integer, String
from sqlalchemy.orm import declarative_base, relationship

from .database import Base

class Exercises(Base):
    __tablename__ = 'exercises'

    id = Column(Integer, Identity(start=1, increment=1), primary_key=True)
    name = Column(String(collation='Latin1_General_CI_AS'), nullable=False)
    category = Column(String(collation='Latin1_General_CI_AS'), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    description = Column(String(collation='Latin1_General_CI_AS'))

    day_exercises = relationship('DayExercises', back_populates='exercise')


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, Identity(start=1, increment=1), primary_key=True)
    email = Column(String(collation='Latin1_General_CI_AS'), nullable=False)
    hashed_password = Column(String(collation='Latin1_General_CI_AS'), nullable=False)
    is_active = Column(Boolean, nullable=False)
    full_name = Column(String(collation='Latin1_General_CI_AS'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user_details = relationship('UserDetails', back_populates='user')
    workout_days = relationship('WorkoutDays', back_populates='user')


class Workouts(Base):
    __tablename__ = 'workouts'

    id = Column(Integer, Identity(start=1, increment=1), primary_key=True)
    name = Column(String(collation='Latin1_General_CI_AS'), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    description = Column(String(collation='Latin1_General_CI_AS'))


class UserDetails(Base):
    __tablename__ = 'user_details'

    id = Column(Integer, Identity(start=1, increment=1), primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    height = Column(Float(53), nullable=False)
    weight = Column(Float(53), nullable=False)
    workout_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    gender = Column(String(collation='Latin1_General_CI_AS'))
    age = Column(Integer)
    fitness_level = Column(String(collation='Latin1_General_CI_AS'))

    user = relationship('Users', back_populates='user_details')


class WorkoutDays(Base):
    __tablename__ = 'workout_days'

    id = Column(Integer, Identity(start=1, increment=1), primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    day = Column(String(collation='Latin1_General_CI_AS'), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    user = relationship('Users', back_populates='workout_days')
    day_exercises = relationship('DayExercises', back_populates='workout_day')


class DayExercises(Base):
    __tablename__ = 'day_exercises'

    id = Column(Integer, Identity(start=1, increment=1), primary_key=True)
    workout_day_id = Column(ForeignKey('workout_days.id'), nullable=False)
    exercise_id = Column(ForeignKey('exercises.id'), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    exercise = relationship('Exercises', back_populates='day_exercises')
    workout_day = relationship('WorkoutDays', back_populates='day_exercises')

    
    



