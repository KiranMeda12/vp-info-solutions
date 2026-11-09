"""
Unit & Integration Test Suite for VP Info Solutions Lead Management System
Verifies clean database initialization and dynamic user management (add/remove RM & SC)
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import SessionLocal
from backend.seed import seed_database
from backend.models import User, Lead, UserRole, LeadStatus, TallyProduct
from backend.schemas import (
    LoginRequest, LeadCreate, LeadUpdateStatus, LeadAssignByAdmin, UserCreate
)
from backend.main import (
    login, get_leads, create_lead, update_lead_status, assign_lead_by_admin,
    get_personal_kpis, get_rm_leaderboard, get_sc_leaderboard, list_users,
    create_user, delete_user, export_powerbi_data
)

def run_tests():
    db = SessionLocal()
    seed_database(db)

    # Clean previous test artifacts if re-running
    db.query(Lead).filter(Lead.business_name == "Dynamic Auto Parts Pvt Ltd").delete()
    db.query(User).filter(User.username.in_(["rm_vikram", "sales_amit", "sc_temp_test"])).delete()
    db.commit()

    print("--- 1. Testing Admin Authentication (Clean Initial Database) ---")
    admin_login = login(LoginRequest(username="admin", password="admin123"), db=db)
    assert admin_login.role == UserRole.ADMIN
    print(f"[PASS] Admin authenticated: {admin_login.full_name} ({admin_login.role})")

    user_admin = db.query(User).filter(User.username == "admin").first()

    print("\n--- 2. Testing Adding New RM via Admin Console ---")
    new_rm = create_user(
        payload=UserCreate(
            full_name="Vikram Malhotra",
            username="rm_vikram",
            password="rm123",
            email="vikram.m@vpinfosolutions.com",
            phone="+91 98111 22334",
            role="RM",
            rm_id=None,
            is_active=True
        ),
        current_user=user_admin,
        db=db
    )
    assert new_rm.username == "rm_vikram"
    assert new_rm.role == "RM"
    print(f"[PASS] Successfully created Relationship Manager: {new_rm.full_name} ({new_rm.username})")

    print("\n--- 3. Testing Adding New Sales Consultant via Admin Console ---")
    new_sc = create_user(
        payload=UserCreate(
            full_name="Amit Verma",
            username="sales_amit",
            password="sales123",
            email="amit.v@vpinfosolutions.com",
            phone="+91 98765 43210",
            role="Sales Consultant",
            rm_id=new_rm.id,
            is_active=True
        ),
        current_user=user_admin,
        db=db
    )
    assert new_sc.username == "sales_amit"
    assert new_sc.rm_id == new_rm.id
    print(f"[PASS] Successfully created Sales Consultant: {new_sc.full_name} (Mapped to RM ID #{new_rm.id})")

    # Verify newly created RM can log in
    rm_login = login(LoginRequest(username="rm_vikram", password="rm123"), db=db)
    assert rm_login.role == UserRole.RM
    print(f"[PASS] RM successfully authenticated with new credentials: {rm_login.full_name}")

    # Verify newly created SC can log in
    sc_login = login(LoginRequest(username="sales_amit", password="sales123"), db=db)
    assert sc_login.role == UserRole.SALES_CONSULTANT
    print(f"[PASS] SC successfully authenticated with new credentials: {sc_login.full_name}")

    user_rm = db.query(User).filter(User.username == "rm_vikram").first()
    user_sc = db.query(User).filter(User.username == "sales_amit").first()

    print("\n--- 4. Testing RM Lead Generation & Admin Assignment ---")
    rm_new_lead = create_lead(
        LeadCreate(
            business_name="Dynamic Auto Parts Pvt Ltd",
            lead_name="Rajesh Gupta",
            designation="Managing Director",
            phone="+91 98220 99887",
            email="rajesh@dynamicauto.in",
            address="MIDC Bhosari, Pune",
            meeting_date="2026-11-25",
            meeting_time="02:00 PM",
            industry="Manufacturing",
            interested_product=TallyProduct.TALLY_PRIME,
            status=LeadStatus.NEW,
            estimated_value=55000.0,
            notes="Interested in multi-user gold license."
        ),
        current_user=user_rm,
        db=db
    )
    assert rm_new_lead.sales_person_id is None, "RM raised lead must initially be unassigned!"
    print(f"[PASS] RM raised lead {rm_new_lead.lead_number} - Status: Pending Admin Assignment")

    # Admin assigns to Sales Consultant
    assigned_lead = assign_lead_by_admin(
        lead_id=rm_new_lead.id,
        payload=LeadAssignByAdmin(sales_person_id=user_sc.id, notes="Assigned to Amit for demo."),
        current_user=user_admin,
        db=db
    )
    assert assigned_lead.sales_person_id == user_sc.id
    print(f"[PASS] Admin assigned lead {assigned_lead.lead_number} to {assigned_lead.sales_person_name}")

    print("\n--- 5. Testing Stage Progression by Sales Consultant ---")
    updated = update_lead_status(
        lead_id=assigned_lead.id,
        payload=LeadUpdateStatus(status=LeadStatus.DEMO_SCHEDULED, notes="Demo confirmed."),
        current_user=user_sc,
        db=db
    )
    assert updated.status == LeadStatus.DEMO_SCHEDULED
    print(f"[PASS] Lead stage progressed to: {updated.status}")

    print("\n--- 6. Testing Removing User Account Safely ---")
    temp_sc = create_user(
        payload=UserCreate(
            full_name="Temporary Rep",
            username="sc_temp_test",
            password="password123",
            email="temp@vpinfo.com",
            role="Sales Consultant",
            rm_id=new_rm.id,
            is_active=True
        ),
        current_user=user_admin,
        db=db
    )
    del_res = delete_user(user_id=temp_sc.id, current_user=user_admin, db=db)
    assert del_res["status"] == "success"
    print(f"[PASS] Successfully deleted user ID #{temp_sc.id}")

    print("\n--- 7. Testing Sales Consultant Standings & Leaderboard Structure ---")
    sc_standings = get_sc_leaderboard(db=db)
    assert len(sc_standings) >= 1
    sc_item = sc_standings[0]
    assert hasattr(sc_item, "sc_name"), "Must have Sales Consultant name"
    assert hasattr(sc_item, "total_assigned"), "Must have Total Assigned"
    assert hasattr(sc_item, "won"), "Must have Won count"
    assert hasattr(sc_item, "not_interested"), "Must have Not Interested count"
    assert hasattr(sc_item, "win_rate"), "Must have Win Rate %"
    assert hasattr(sc_item, "price_on_win"), "Must have Price on Win (₹)"
    print(f"[PASS] SC Standings schema verified: {sc_item.sc_name} | Assigned: {sc_item.total_assigned} | Won: {sc_item.won} | Not Interested: {sc_item.not_interested} | Win Rate: {sc_item.win_rate}% | Price on Win: Rs {sc_item.price_on_win}")

    # Teardown test artifacts so database stays clean
    db.query(Lead).filter(Lead.business_name == "Dynamic Auto Parts Pvt Ltd").delete()
    db.query(User).filter(User.username.in_(["rm_vikram", "sales_amit", "sc_temp_test"])).delete()
    db.commit()

    print("\n============================================================")
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("============================================================")

if __name__ == "__main__":
    run_tests()
