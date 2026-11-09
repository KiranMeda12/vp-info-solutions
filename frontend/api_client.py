"""
VP Info Solutions Pvt Ltd - Lead Management System
Frontend API Client wrapper
"""

import requests
from typing import Dict, Any, Optional, List

API_BASE_URL = "http://127.0.0.1:8000/api"


class APIClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def set_token(self, token: str):
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"

    def login(self, username: str, password: str) -> Dict[str, Any]:
        resp = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            self.set_token(data["access_token"])
            return {"success": True, "data": data}
        try:
            err = resp.json().get("detail", "Login failed")
        except Exception:
            err = f"HTTP {resp.status_code}: {resp.text}"
        return {"success": False, "error": err}

    def get_me(self) -> Dict[str, Any]:
        resp = requests.get(f"{API_BASE_URL}/auth/me", headers=self.headers, timeout=10)
        return resp.json() if resp.status_code == 200 else {}

    def get_leads(
        self,
        status: Optional[str] = None,
        product: Optional[str] = None,
        search: Optional[str] = None,
        sales_rep_id: Optional[int] = None,
        rm_id: Optional[int] = None,
        unassigned_only: Optional[bool] = False,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        params = {}
        if status and status != "All":
            params["status_filter"] = status
        if product and product != "All":
            params["product_filter"] = product
        if search:
            params["search"] = search
        if sales_rep_id:
            params["sales_rep_id"] = sales_rep_id
        if rm_id:
            params["rm_id"] = rm_id
        if unassigned_only:
            params["unassigned_only"] = True
        if year:
            params["year"] = year
        if month:
            params["month"] = month

        resp = requests.get(f"{API_BASE_URL}/leads", headers=self.headers, params=params, timeout=10)
        return resp.json() if resp.status_code == 200 else []

    def create_lead(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(f"{API_BASE_URL}/leads", headers=self.headers, json=payload, timeout=10)
        if resp.status_code in (200, 201):
            return {"success": True, "data": resp.json()}
        try:
            err = resp.json().get("detail", "Failed to create lead")
        except Exception:
            err = resp.text
        return {"success": False, "error": err}

    def assign_lead(self, lead_id: int, sales_person_id: int, notes: Optional[str] = None) -> Dict[str, Any]:
        resp = requests.post(
            f"{API_BASE_URL}/leads/{lead_id}/assign",
            headers=self.headers,
            json={"sales_person_id": sales_person_id, "notes": notes},
            timeout=10
        )
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        try:
            err = resp.json().get("detail", "Failed to assign lead")
        except Exception:
            err = resp.text
        return {"success": False, "error": err}

    def update_lead_status(self, lead_id: int, new_status: str, notes: Optional[str] = None, estimated_value: Optional[float] = None) -> Dict[str, Any]:
        payload = {"status": new_status, "notes": notes}
        if estimated_value is not None:
            payload["estimated_value"] = estimated_value
        resp = requests.patch(
            f"{API_BASE_URL}/leads/{lead_id}/status",
            headers=self.headers,
            json=payload,
            timeout=10
        )
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        try:
            err = resp.json().get("detail", "Failed to update status")
        except Exception:
            err = resp.text
        return {"success": False, "error": err}

    def get_personal_kpis(self) -> Dict[str, Any]:
        resp = requests.get(f"{API_BASE_URL}/kpis/personal", headers=self.headers, timeout=10)
        return resp.json() if resp.status_code == 200 else {}

    def get_rm_leaderboard(self) -> List[Dict[str, Any]]:
        resp = requests.get(f"{API_BASE_URL}/leaderboard/rm", headers=self.headers, timeout=10)
        return resp.json() if resp.status_code == 200 else []

    def get_sc_leaderboard(self) -> List[Dict[str, Any]]:
        resp = requests.get(f"{API_BASE_URL}/leaderboard/sc", headers=self.headers, timeout=10)
        return resp.json() if resp.status_code == 200 else []

    def get_users(self, role: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"role": role} if role else {}
        resp = requests.get(f"{API_BASE_URL}/users", headers=self.headers, params=params, timeout=10)
        return resp.json() if resp.status_code == 200 else []

    def create_user(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(f"{API_BASE_URL}/users", headers=self.headers, json=payload, timeout=10)
        if resp.status_code in (200, 201):
            return {"success": True, "data": resp.json()}
        try:
            err = resp.json().get("detail", "Failed to create user")
        except Exception:
            err = resp.text
        return {"success": False, "error": err}

    def update_user(self, user_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.put(f"{API_BASE_URL}/users/{user_id}", headers=self.headers, json=payload, timeout=10)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        try:
            err = resp.json().get("detail", "Failed to update user")
        except Exception:
            err = resp.text
        return {"success": False, "error": err}

    def delete_user(self, user_id: int) -> Dict[str, Any]:
        resp = requests.delete(f"{API_BASE_URL}/users/{user_id}", headers=self.headers, timeout=10)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        try:
            err = resp.json().get("detail", "Failed to delete user")
        except Exception:
            err = resp.text
        return {"success": False, "error": err}
