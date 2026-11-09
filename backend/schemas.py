"""
VP Info Solutions Pvt Ltd - Lead Management System
Pydantic Schemas for Request & Response Serialization
"""

import datetime
from typing import Optional, List
from pydantic import BaseModel


# ---------------------- AUTH SCHEMAS ----------------------
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id: int
    user_id: int
    username: str
    full_name: str
    role: str
    email: str
    rm_id: Optional[int] = None
    rm_name: Optional[str] = None


# ---------------------- USER SCHEMAS ----------------------
class UserBase(BaseModel):
    username: str
    full_name: str
    email: str
    phone: Optional[str] = None
    role: str
    rm_id: Optional[int] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    rm_id: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    email: str
    phone: Optional[str] = None
    role: str
    rm_id: Optional[int] = None
    rm_name: Optional[str] = None
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ---------------------- LEAD SCHEMAS ----------------------
class LeadBase(BaseModel):
    business_name: str
    lead_name: str
    designation: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    meeting_date: Optional[str] = None
    meeting_time: Optional[str] = None
    industry: Optional[str] = "Corporate"
    interested_product: str
    status: Optional[str] = "New"
    estimated_value: Optional[float] = 0.0
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    sales_person_id: Optional[int] = None


class LeadUpdateStatus(BaseModel):
    status: str
    notes: Optional[str] = None
    estimated_value: Optional[float] = None


class LeadAssignByAdmin(BaseModel):
    sales_person_id: int
    notes: Optional[str] = None


class LeadResponse(BaseModel):
    id: int
    lead_number: str
    business_name: str
    lead_name: str
    designation: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    meeting_date: Optional[str] = None
    meeting_time: Optional[str] = None
    industry: str
    interested_product: str
    status: str
    estimated_value: float
    notes: Optional[str] = None
    created_by_id: Optional[int] = None
    created_by_name: Optional[str] = None
    created_by_role: Optional[str] = None
    sales_person_id: Optional[int] = None
    sales_person_name: Optional[str] = None
    rm_id: Optional[int] = None
    rm_name: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


# ---------------------- LEADERBOARD & KPI SCHEMAS ----------------------
class PersonalKPIs(BaseModel):
    my_total_leads: int
    my_open_deals: int
    my_closed_won: int
    my_closed_lost: int
    my_win_rate: float
    my_total_pipeline_value: float


class RMLeaderboardItem(BaseModel):
    rm_id: int
    rm_name: str
    leads_raised: int
    team_reps_count: int
    team_total_leads: int
    team_closed_won: int
    team_conversion_rate: float
    team_pipeline_value: float


class SCLeaderboardItem(BaseModel):
    sc_id: int
    sc_name: str
    rm_name: Optional[str] = None
    total_leads: int
    total_assigned: int
    open_deals: int
    closed_won: int
    won: int
    closed_lost: int
    not_interested: int
    win_rate: float
    pipeline_value: float
    price_on_win: float
