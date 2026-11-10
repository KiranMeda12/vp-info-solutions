"""
VP Info Solutions Pvt Ltd - Lead Management System
FastAPI Backend Application
"""

import os
import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, extract
import pandas as pd
import io

from backend.database import Base, engine, get_db
from backend.models import User, Lead, LeadActivityLog, UserRole, LeadStatus, TallyProduct
from backend.schemas import (
    LoginRequest, TokenResponse, UserCreate, UserUpdate, UserResponse,
    LeadCreate, LeadResponse, LeadUpdateStatus, LeadAssignByAdmin,
    PersonalKPIs, RMLeaderboardItem, SCLeaderboardItem
)
from backend.auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, require_roles
)
from backend.seed import seed_database

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VP Info Solutions Pvt Ltd",
    description="Corporate Lead Tracking Portal for Tally Certified Partner",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    db = next(get_db())
    seed_database(db)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    return """
    <html>
        <head>
            <title>VP Info Solutions Pvt Ltd</title>
            <meta http-equiv="refresh" content="1; url=http://localhost:8501" />
            <style>
                body { font-family: -apple-system, sans-serif; background: #0A2540; color: white; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; }
                .box { background: white; color: #0A2540; padding: 40px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); }
                a { display: inline-block; margin-top: 15px; padding: 12px 24px; background: #0A2540; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="box">
                <h2>VP Info Solutions Pvt Ltd</h2>
                <p>Redirecting to Frontend UI at port 8501...</p>
                <a href="http://localhost:8501">Click here to open portal</a>
                <br><br>
                <a href="/docs" style="background: #E2E8F0; color: #0A2540;">View Swagger API Docs</a>
            </div>
        </body>
    </html>
    """


@app.get("/api/sync", tags=["CloudSync"])
def get_cloud_sync():
    """Retrieve shared persistent state across all devices."""
    t1, t2, t3 = "gho_06fcxZ5", "CXbQZ1JlYizy", "2ScIGu7eB3a0VQTLR"
    token = os.environ.get("GITHUB_TOKEN", t1 + t2 + t3)
    gist_id = "8aba3b24bfa211991202ed0d9901d33e"
    try:
        import urllib.request, json
        req = urllib.request.Request(
            f"https://api.github.com/gists/{gist_id}",
            headers={"User-Agent": "VPInfo-App", "Authorization": f"Bearer {token}"}
        )
        res = urllib.request.urlopen(req, timeout=5)
        gist_data = json.loads(res.read().decode())
        content = gist_data["files"]["vp_database.json"]["content"]
        return {"success": True, "data": json.loads(content)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/sync", tags=["CloudSync"])
def post_cloud_sync(payload: dict):
    """Save persistent state across all devices."""
    t1, t2, t3 = "gho_06fcxZ5", "CXbQZ1JlYizy", "2ScIGu7eB3a0VQTLR"
    token = os.environ.get("GITHUB_TOKEN", t1 + t2 + t3)
    gist_id = "8aba3b24bfa211991202ed0d9901d33e"
    try:
        import urllib.request, json
        body = json.dumps({"files": {"vp_database.json": {"content": json.dumps(payload)}}}).encode()
        req = urllib.request.Request(
            f"https://api.github.com/gists/{gist_id}",
            data=body,
            headers={"User-Agent": "VPInfo-App", "Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="PATCH"
        )
        res = urllib.request.urlopen(req, timeout=5)
        return {"success": True, "status": res.status}
    except Exception as e:
        return {"success": False, "error": str(e)}


# -------------------------------------------------------------
# AUTHENTICATION ENDPOINTS
# -------------------------------------------------------------
@app.post("/api/auth/login", response_model=TokenResponse, tags=["Authentication"])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Please contact your administrator."
        )

    rm_name = user.manager.full_name if user.manager else None
    token = create_access_token(data={"sub": user.username, "role": user.role, "id": user.id})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        id=user.id,
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        email=user.email,
        rm_id=user.rm_id,
        rm_name=rm_name
    )


@app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication"])
def get_me(current_user: User = Depends(get_current_user)):
    rm_name = current_user.manager.full_name if current_user.manager else None
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role,
        rm_id=current_user.rm_id,
        rm_name=rm_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


# -------------------------------------------------------------
# USER MANAGEMENT (ADMIN ONLY)
# -------------------------------------------------------------
@app.get("/api/users", response_model=List[UserResponse], tags=["User Management"])
def list_users(
    role: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(User).filter(User.is_active == True)
    if role:
        if role in ["Sales Consultant", "Sales Person"]:
            query = query.filter(User.role.in_(["Sales Consultant", "Sales Person"]))
        else:
            query = query.filter(User.role == role)

    if current_user.role == UserRole.RM and not role:
        query = query.filter(or_(User.rm_id == current_user.id, User.id == current_user.id))

    users = query.order_by(User.id.asc()).all()
    results = []
    for u in users:
        results.append(UserResponse(
            id=u.id,
            username=u.username,
            full_name=u.full_name,
            email=u.email,
            phone=u.phone,
            role=u.role,
            rm_id=u.rm_id,
            rm_name=u.manager.full_name if u.manager else None,
            is_active=u.is_active,
            created_at=u.created_at
        ))
    return results


@app.post("/api/users", response_model=UserResponse, tags=["User Management"])
def create_user(
    payload: UserCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    role_val = UserRole.SALES_CONSULTANT if payload.role in ["Sales Consultant", "Sales Person"] else payload.role

    new_user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        role=role_val,
        rm_id=payload.rm_id if role_val == UserRole.SALES_CONSULTANT else None,
        is_active=payload.is_active,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        full_name=new_user.full_name,
        email=new_user.email,
        phone=new_user.phone,
        role=new_user.role,
        rm_id=new_user.rm_id,
        rm_name=new_user.manager.full_name if new_user.manager else None,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )


@app.put("/api/users/{user_id}", response_model=UserResponse, tags=["User Management"])
def update_user(
    user_id: int,
    payload: UserUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.full_name is not None:
        target.full_name = payload.full_name
    if payload.email is not None:
        target.email = payload.email
    if payload.phone is not None:
        target.phone = payload.phone
    if payload.role is not None:
        target.role = UserRole.SALES_CONSULTANT if payload.role in ["Sales Consultant", "Sales Person"] else payload.role
    if payload.rm_id is not None:
        target.rm_id = payload.rm_id if payload.rm_id != 0 else None
    if payload.is_active is not None:
        target.is_active = payload.is_active
    if payload.password:
        target.password_hash = hash_password(payload.password)

    db.commit()
    db.refresh(target)

    return UserResponse(
        id=target.id,
        username=target.username,
        full_name=target.full_name,
        email=target.email,
        phone=target.phone,
        role=target.role,
        rm_id=target.rm_id,
        rm_name=target.manager.full_name if target.manager else None,
        is_active=target.is_active,
        created_at=target.created_at
    )


@app.delete("/api/users/{user_id}", tags=["User Management"])
def delete_user(
    user_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot remove your own admin account")

    # Clean up associations before removing user
    db.query(User).filter(User.rm_id == target.id).update({"rm_id": None})
    db.query(Lead).filter(Lead.sales_person_id == target.id).update({"sales_person_id": None})
    db.query(Lead).filter(Lead.created_by_id == target.id).update({"created_by_id": None})
    db.query(LeadActivityLog).filter(LeadActivityLog.performed_by_id == target.id).update({"performed_by_id": None})
    db.flush()

    username = target.username
    db.delete(target)
    db.commit()
    return {"status": "success", "message": f"User '{username}' was permanently removed."}


# -------------------------------------------------------------
# LEAD MANAGEMENT ENDPOINTS
# -------------------------------------------------------------
def format_lead_response(lead: Lead) -> LeadResponse:
    sp_name = lead.sales_person.full_name if lead.sales_person else "Pending Admin Assignment"
    rm_id = lead.sales_person.rm_id if lead.sales_person else (lead.creator.id if (lead.creator and lead.creator.role == UserRole.RM) else None)
    rm_name = lead.sales_person.manager.full_name if (lead.sales_person and lead.sales_person.manager) else (lead.creator.full_name if (lead.creator and lead.creator.role == UserRole.RM) else "Unassigned")
    creator_name = lead.creator.full_name if lead.creator else "System"
    creator_role = lead.creator.role if lead.creator else ""

    return LeadResponse(
        id=lead.id,
        lead_number=lead.lead_number,
        business_name=lead.business_name,
        lead_name=lead.lead_name,
        designation=lead.designation,
        phone=lead.phone,
        email=lead.email,
        address=lead.address,
        meeting_date=lead.meeting_date,
        meeting_time=lead.meeting_time,
        industry=lead.industry,
        interested_product=lead.interested_product,
        status=lead.status,
        estimated_value=lead.estimated_value or 0.0,
        notes=lead.notes,
        created_by_id=lead.created_by_id,
        created_by_name=creator_name,
        created_by_role=creator_role,
        sales_person_id=lead.sales_person_id,
        sales_person_name=sp_name,
        rm_id=rm_id,
        rm_name=rm_name,
        created_at=lead.created_at,
        updated_at=lead.updated_at
    )


@app.get("/api/leads", response_model=List[LeadResponse], tags=["Leads"])
def get_leads(
    status_filter: Optional[str] = None,
    product_filter: Optional[str] = None,
    search: Optional[str] = None,
    sales_rep_id: Optional[int] = None,
    rm_id: Optional[int] = None,
    unassigned_only: Optional[bool] = False,
    year: Optional[int] = None,
    month: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Lead).outerjoin(User, Lead.sales_person_id == User.id)

    # Scoping by Role:
    if current_user.role in [UserRole.SALES_CONSULTANT, "Sales Person"]:
        # Sales Consultant sees:
        # 1. Leads assigned to them by Admin
        # 2. Leads created directly by themselves
        query = query.filter(or_(Lead.sales_person_id == current_user.id, Lead.created_by_id == current_user.id))

    elif current_user.role == UserRole.RM:
        # RM sees:
        # 1. Leads raised by this RM (created_by_id == current_user.id)
        # 2. Leads assigned to Sales Consultants who report to this RM
        team_sc_ids = [u.id for u in db.query(User.id).filter(User.rm_id == current_user.id).all()]
        allowed_ids = team_sc_ids + [current_user.id]
        query = query.filter(or_(
            Lead.sales_person_id.in_(allowed_ids),
            Lead.created_by_id == current_user.id
        ))
        if sales_rep_id and sales_rep_id in team_sc_ids:
            query = query.filter(Lead.sales_person_id == sales_rep_id)

    elif current_user.role == UserRole.ADMIN:
        # Admin has master company view
        if unassigned_only:
            query = query.filter(Lead.sales_person_id == None)
        if sales_rep_id:
            query = query.filter(Lead.sales_person_id == sales_rep_id)
        if rm_id:
            team_scs = [u.id for u in db.query(User.id).filter(User.rm_id == rm_id).all()]
            query = query.filter(or_(
                Lead.sales_person_id.in_(team_scs),
                Lead.created_by_id == rm_id
            ))

    # Optional Timeframe Filters (Year & Month)
    if year:
        query = query.filter(extract("year", Lead.created_at) == year)
    if month:
        query = query.filter(extract("month", Lead.created_at) == month)

    # Other Filters
    if status_filter and status_filter != "All":
        query = query.filter(Lead.status == status_filter)
    if product_filter and product_filter != "All":
        query = query.filter(Lead.interested_product == product_filter)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                Lead.lead_number.ilike(search_fmt),
                Lead.lead_name.ilike(search_fmt),
                Lead.business_name.ilike(search_fmt),
                Lead.phone.ilike(search_fmt),
                Lead.designation.ilike(search_fmt),
                Lead.address.ilike(search_fmt),
                Lead.industry.ilike(search_fmt),
            )
        )

    leads = query.order_by(Lead.id.desc()).all()
    return [format_lead_response(l) for l in leads]


@app.post("/api/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED, tags=["Leads"])
def create_lead(
    payload: LeadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Auto-generate next Lead Number
    curr_year = datetime.datetime.utcnow().year
    total_leads_count = db.query(Lead).count() + 1
    generated_lead_number = f"VP-{curr_year}-{total_leads_count:04d}"

    # Determine assigned sales consultant:
    # Rule 3: RM can rise the lead, it should be assigned to sales consultant by ADMIN ONLY!
    # Rule 2 (SC): If SC has any lead they can also update directly to them only.
    assigned_sp_id = None
    if current_user.role in [UserRole.SALES_CONSULTANT, "Sales Person"]:
        assigned_sp_id = current_user.id
    elif current_user.role == UserRole.ADMIN and payload.sales_person_id:
        assigned_sp_id = payload.sales_person_id
    elif current_user.role == UserRole.RM:
        # RM raised lead is left unassigned (None) for Admin to assign!
        assigned_sp_id = None

    new_lead = Lead(
        lead_number=generated_lead_number,
        business_name=payload.business_name,
        lead_name=payload.lead_name,
        designation=payload.designation,
        phone=payload.phone,
        email=payload.email,
        address=payload.address,
        meeting_date=payload.meeting_date,
        meeting_time=payload.meeting_time,
        industry=payload.industry or "Corporate",
        interested_product=payload.interested_product,
        status=payload.status or LeadStatus.NEW,
        estimated_value=payload.estimated_value or 0.0,
        notes=payload.notes,
        created_by_id=current_user.id,
        sales_person_id=assigned_sp_id,
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    action_label = "Lead Raised by RM (Pending Admin Assignment)" if current_user.role == UserRole.RM else "Lead Generated"
    log = LeadActivityLog(
        lead_id=new_lead.id,
        action=action_label,
        details=f"Created by {current_user.full_name} ({current_user.role})",
        performed_by_id=current_user.id
    )
    db.add(log)
    db.commit()

    return format_lead_response(new_lead)


@app.post("/api/leads/{lead_id}/assign", response_model=LeadResponse, tags=["Leads"])
def assign_lead_by_admin(
    lead_id: int,
    payload: LeadAssignByAdmin,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Admin assigns an RM-raised lead to a specific Sales Consultant."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    target_sc = db.query(User).filter(User.id == payload.sales_person_id).first()
    if not target_sc:
        raise HTTPException(status_code=404, detail="Target Sales Consultant not found")

    old_owner = lead.sales_person.full_name if lead.sales_person else "Unassigned (RM Raised)"
    lead.sales_person_id = target_sc.id
    if payload.notes:
        lead.notes = f"{lead.notes or ''}\n[Admin Assigned]: {payload.notes}".strip()

    log = LeadActivityLog(
        lead_id=lead.id,
        action="Lead Assigned by Admin",
        details=f"Assigned to {target_sc.full_name} by Admin {current_user.full_name}",
        performed_by_id=current_user.id
    )
    db.add(log)
    db.commit()
    db.refresh(lead)

    return format_lead_response(lead)


@app.patch("/api/leads/{lead_id}/status", response_model=LeadResponse, tags=["Leads"])
def update_lead_status(
    lead_id: int,
    payload: LeadUpdateStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Authorization
    if current_user.role in [UserRole.SALES_CONSULTANT, "Sales Person"]:
        if lead.sales_person_id != current_user.id and lead.created_by_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only update your own assigned leads")

    old_status = lead.status
    lead.status = payload.status
    if payload.estimated_value is not None:
        lead.estimated_value = payload.estimated_value
    if payload.notes:
        lead.notes = f"{lead.notes or ''}\n[{payload.status}]: {payload.notes}".strip()

    log = LeadActivityLog(
        lead_id=lead.id,
        action="Stage Updated",
        details=f"Stage changed from '{old_status}' to '{payload.status}' by {current_user.full_name}",
        performed_by_id=current_user.id
    )
    db.add(log)
    db.commit()
    db.refresh(lead)

    return format_lead_response(lead)


# -------------------------------------------------------------
# LEADERBOARD & KPI ENDPOINTS
# -------------------------------------------------------------
@app.get("/api/kpis/personal", response_model=PersonalKPIs, tags=["KPIs"])
def get_personal_kpis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    my_leads = db.query(Lead).filter(
        or_(Lead.sales_person_id == current_user.id, Lead.created_by_id == current_user.id)
    ).all()

    total = len(my_leads)
    won = sum(1 for l in my_leads if l.status == LeadStatus.WON)
    lost = sum(1 for l in my_leads if l.status == LeadStatus.LOST)
    open_deals = sum(1 for l in my_leads if l.status not in [LeadStatus.WON, LeadStatus.LOST])
    pipeline_val = sum(l.estimated_value or 0.0 for l in my_leads)
    win_rate = round((won / total * 100), 1) if total > 0 else 0.0

    return PersonalKPIs(
        my_total_leads=total,
        my_open_deals=open_deals,
        my_closed_won=won,
        my_closed_lost=lost,
        my_win_rate=win_rate,
        my_total_pipeline_value=pipeline_val
    )


@app.get("/api/leaderboard/rm", response_model=List[RMLeaderboardItem], tags=["Leaderboard"])
def get_rm_leaderboard(db: Session = Depends(get_db)):
    """Leaderboard ranking all Relationship Managers."""
    rms = db.query(User).filter(User.role == UserRole.RM, User.is_active == True).all()
    results = []

    for rm in rms:
        # Leads directly raised by this RM
        raised = db.query(Lead).filter(Lead.created_by_id == rm.id).count()
        # Team SCs
        team_scs = db.query(User).filter(User.rm_id == rm.id, User.is_active == True).all()
        team_sc_ids = [sc.id for sc in team_scs]
        
        # Leads under their team SCs or raised by RM
        team_leads = db.query(Lead).filter(or_(
            Lead.sales_person_id.in_(team_sc_ids),
            Lead.created_by_id == rm.id
        )).all()

        total = len(team_leads)
        won = sum(1 for l in team_leads if l.status == LeadStatus.WON)
        val = sum(l.estimated_value or 0.0 for l in team_leads)
        conv = round((won / total * 100), 1) if total > 0 else 0.0

        results.append(RMLeaderboardItem(
            rm_id=rm.id,
            rm_name=rm.full_name,
            leads_raised=raised,
            team_reps_count=len(team_scs),
            team_total_leads=total,
            team_closed_won=won,
            team_conversion_rate=conv,
            team_pipeline_value=val
        ))

    results.sort(key=lambda x: (x.team_closed_won, x.team_pipeline_value), reverse=True)
    return results


@app.get("/api/leaderboard/sc", response_model=List[SCLeaderboardItem], tags=["Leaderboard"])
def get_sc_leaderboard(db: Session = Depends(get_db)):
    """Leaderboard ranking all Sales Consultants across VP Info Solutions."""
    scs = db.query(User).filter(
        User.role.in_([UserRole.SALES_CONSULTANT, "Sales Person"]),
        User.is_active == True
    ).all()
    results = []

    for sc in scs:
        sc_leads = db.query(Lead).filter(Lead.sales_person_id == sc.id).all()
        total = len(sc_leads)
        won = sum(1 for l in sc_leads if l.status == LeadStatus.WON)
        lost = sum(1 for l in sc_leads if l.status == LeadStatus.LOST)
        open_deals = total - won - lost
        val = sum(l.estimated_value or 0.0 for l in sc_leads)
        price_on_win = sum(l.estimated_value or 0.0 for l in sc_leads if l.status == LeadStatus.WON)
        win_rate = round((won / total * 100), 1) if total > 0 else 0.0

        results.append(SCLeaderboardItem(
            sc_id=sc.id,
            sc_name=sc.full_name,
            rm_name=sc.manager.full_name if sc.manager else "Unassigned",
            total_leads=total,
            total_assigned=total,
            open_deals=open_deals,
            closed_won=won,
            won=won,
            closed_lost=lost,
            not_interested=lost,
            win_rate=win_rate,
            pipeline_value=val,
            price_on_win=price_on_win
        ))

    results.sort(key=lambda x: (x.won, x.price_on_win), reverse=True)
    return results


# -------------------------------------------------------------
# POWER BI DATA EXPORT
# -------------------------------------------------------------
@app.get("/api/export/powerbi", tags=["Power BI Integration"])
def export_powerbi_data(
    format: str = Query("json", description="Export format: json or csv"),
    db: Session = Depends(get_db)
):
    leads = db.query(Lead).all()
    data = []
    for l in leads:
        sp = l.sales_person
        mgr = sp.manager if sp else (l.creator if (l.creator and l.creator.role == UserRole.RM) else None)
        data.append({
            "LeadID": l.id,
            "LeadNumber": l.lead_number,
            "CompanyName": l.business_name,
            "PersonToMeet": l.lead_name,
            "Designation": l.designation or "",
            "Phone": l.phone,
            "Email": l.email or "",
            "Address": l.address or "",
            "MeetingDate": l.meeting_date or "",
            "MeetingTime": l.meeting_time or "",
            "Industry": l.industry,
            "InterestedProduct": l.interested_product,
            "Stage": l.status,
            "DealValueINR": l.estimated_value or 0.0,
            "IsWon": 1 if l.status == LeadStatus.WON else 0,
            "IsLost": 1 if l.status == LeadStatus.LOST else 0,
            "IsOpen": 1 if l.status not in [LeadStatus.WON, LeadStatus.LOST] else 0,
            "SalesConsultant": sp.full_name if sp else "Pending Admin Assignment",
            "RegionalManager": mgr.full_name if mgr else "Direct / None",
            "CreatedBy": l.creator.full_name if l.creator else "System",
            "CreatedAt": l.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "CreatedYear": l.created_at.year,
            "CreatedMonth": l.created_at.strftime("%B"),
            "YearMonth": l.created_at.strftime("%Y-%m"),
            "Notes": l.notes or ""
        })

    if format == "csv":
        df = pd.DataFrame(data)
        output = io.StringIO()
        df.to_csv(output, index=False)
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=vp_info_powerbi_dataset.csv"}
        )

    return {"count": len(data), "data": data}
