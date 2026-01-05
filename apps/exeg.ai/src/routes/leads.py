"""
Leads/Registration Routes
Endpoints para captura de leads do site institucional
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api", tags=["Leads"])

# Database path
LEADS_DB_PATH = Path(__file__).parent.parent.parent / "data" / "leads.db"


def get_db_connection():
    """Get database connection with row factory."""
    LEADS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(LEADS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_leads_db():
    """Initialize leads database tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users/Leads table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Downloads/Tracking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            page TEXT NOT NULL,
            downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email)
        )
    """)

    conn.commit()
    conn.close()


# Initialize on module load
init_leads_db()


# ==================== Models ====================

class LeadRegister(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None


class LeadDownload(BaseModel):
    email: EmailStr
    page: str


class LeadResponse(BaseModel):
    success: bool
    message: str
    lead_id: Optional[int] = None


# ==================== Endpoints ====================

@router.post("/register", response_model=LeadResponse)
async def register_lead(lead: LeadRegister):
    """
    Register a new lead/subscriber.
    Used by leads-capture.js on the institutional site.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (lead.email,))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            return LeadResponse(
                success=True,
                message="Email ja cadastrado. Bem-vindo de volta!",
                lead_id=existing["id"]
            )

        # Insert new lead
        cursor.execute(
            "INSERT INTO users (name, email, phone) VALUES (?, ?, ?)",
            (lead.name, lead.email, lead.phone)
        )
        lead_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return LeadResponse(
            success=True,
            message="Cadastro realizado com sucesso!",
            lead_id=lead_id
        )

    except sqlite3.IntegrityError:
        return LeadResponse(
            success=True,
            message="Email ja cadastrado.",
            lead_id=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download")
async def track_download(download: LeadDownload):
    """
    Track a download/page access by a lead.
    Used for source attribution.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO downloads (user_email, page) VALUES (?, ?)",
            (download.email, download.page)
        )
        conn.commit()
        conn.close()

        return {"success": True}

    except Exception as e:
        # Silently fail for tracking
        return {"success": False, "error": str(e)}


@router.get("/leads/count")
async def leads_count():
    """Get total lead count for stats."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM users")
        total = cursor.fetchone()["total"]

        # Today's count
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            "SELECT COUNT(*) as today FROM users WHERE DATE(registered_at) = ?",
            (today,)
        )
        today_count = cursor.fetchone()["today"]

        conn.close()

        return {
            "total": total,
            "today": today_count
        }

    except Exception as e:
        return {"total": 0, "today": 0, "error": str(e)}
