import uuid
from typing import Any
import crud 
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select
#from sql import database, models, schemas
from api.deps import SessionDep





