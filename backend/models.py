"""
VP Info Solutions Pvt Ltd - Lead Management System
SQLAlchemy Database Models
"""

import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
)
from sqlalchemy.orm import relationship
from backend.database import Base


class UserRole:
    ADMIN = "Admin"
    RM = "RM"
    SALES_CONSULTANT = "Sales Consultant"
    ALL = [ADMIN, RM, SALES_CONSULTANT]


class LeadStatus:
    NEW = "New"
    CONTACTED = "Contacted"
    DEMO_SCHEDULED = "Demo Scheduled"
    NEGOTIATION = "Negotiation"
    WON = "Won"
    LOST = "Lost"
    ALL = [NEW, CONTACTED, DEMO_SCHEDULED, NEGOTIATION, WON, LOST]


class TallyProduct:
    TALLY_PRIME = "TallyPrime Silver/Gold"
    TALLY_ERP9_UPGRADE = "Tally.ERP 9 Upgrade to Prime"
    TALLY_CUSTOMIZATION = "Tally Customization (TDL)"
    TALLY_AMC = "Annual Maintenance Contract (AMC)"
    TALLY_ON_CLOUD = "Tally on Cloud"
    TALLY_SERVER_9 = "Tally Server 9"
    TALLY_INTEGRATION = "Tally API & ERP Integration"
    ALL = [
        TALLY_PRIME,
        TALLY_ERP9_UPGRADE,
        TALLY_CUSTOMIZATION,
        TALLY_AMC,
        TALLY_ON_CLOUD,
        TALLY_SERVER_9,
        TALLY_INTEGRATION,
    ]


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(String(30), nullable=False)  # Admin, RM, Sales Consultant
    is_active = Column(Boolean, default=True)
    
    # Self-referential relationship: Sales Consultant maps to their RM (Relationship Manager)
    rm_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    manager = relationship("User", remote_side=[id], backref="reporting_reps")
    leads_assigned = relationship("Lead", back_populates="sales_person", foreign_keys="Lead.sales_person_id")
    leads_created = relationship("Lead", back_populates="creator", foreign_keys="Lead.created_by_id")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lead_number = Column(String(30), unique=True, index=True, nullable=False)  # Auto-generated e.g. VP-2026-0001
    business_name = Column(String(150), nullable=False)  # Name of company
    lead_name = Column(String(100), nullable=False)      # Name of the person to meet
    designation = Column(String(80), nullable=True)      # Designation
    phone = Column(String(20), nullable=False)           # Contact Number
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)                # Company / Meeting Address
    meeting_date = Column(String(30), nullable=True)     # Meeting Date
    meeting_time = Column(String(30), nullable=True)     # Meeting Timings
    industry = Column(String(80), nullable=False, default="Corporate")
    interested_product = Column(String(100), nullable=False) # Which product they are interested
    status = Column(String(30), default=LeadStatus.NEW, nullable=False)
    estimated_value = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    
    # Tracking creator (RM or SC)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Lead assignment: When RM raises lead, this is NULL until assigned to a Sales Consultant by Admin!
    sales_person_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    sales_person = relationship("User", back_populates="leads_assigned", foreign_keys=[sales_person_id])
    creator = relationship("User", back_populates="leads_created", foreign_keys=[created_by_id])
    history = relationship("LeadActivityLog", back_populates="lead", cascade="all, delete-orphan")


class LeadActivityLog(Base):
    __tablename__ = "lead_activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False)
    details = Column(Text, nullable=True)
    performed_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    lead = relationship("Lead", back_populates="history")
    performed_by = relationship("User")
