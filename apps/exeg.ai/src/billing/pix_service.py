"""
PIX payment service for Otimiza Pagamentos.
Modelo Binance: usuário envia comprovante via WhatsApp para validação pela ANA.
"""
import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from sqlalchemy.orm import Session

from src.config.settings import settings
from src.models.db_models import User, PixTransaction
from .plans import CREDIT_PACKAGES, CreditPackage, calculate_package_credits, format_price
from .credit_service import credit_service


class PixService:
    """
    Service for PIX payments via Otimiza Pagamentos (OtimizaPro).

    A OtimizaPro é uma WorkTech brasileira especializada em benefícios e
    pagamentos corporativos. Pioneira na Gestão Inteligente de Vale-Transporte.

    Escritório: Alameda Vicente Pinzon, 54 - Vila Olímpia, São Paulo - Cubo Itaú
    """

    # Chave PIX da Otimiza Pagamentos
    PIX_KEY = "pix@otimizapagamentos.com.br"
    PIX_KEY_TYPE = "email"
    BENEFICIARY_NAME = "OTIMIZA PAGAMENTOS LTDA"
    BENEFICIARY_CITY = "SAO PAULO"

    # WhatsApp da Otimiza (ANA - IA de validação)
    WHATSAPP_NUMBER = "+5521994487472"  # Canal oficial Otimiza Na Meta
    WHATSAPP_MESSAGE_TEMPLATE = """
🔔 *Comprovante de Pagamento - exeg.ai*

Olá! Recebi seu comprovante de pagamento PIX.

📋 *Detalhes do Pedido:*
• ID: {transaction_id}
• Valor: {amount}
• Créditos: {credits}
• Usuário: {user_email}

Por favor, envie o comprovante do PIX em resposta a esta mensagem.
A validação será feita automaticamente pela ANA.

_Tempo máximo para envio: 24 horas_
"""

    def __init__(self):
        """Initialize PIX service."""
        self._whatsapp_number = getattr(settings, "OTIMIZA_WHATSAPP", self.WHATSAPP_NUMBER)
        self._webhook_secret = getattr(settings, "OTIMIZA_WEBHOOK_SECRET", None)

    def generate_pix_code(
        self,
        amount_cents: int,
        transaction_id: str,
        description: str = "Creditos exeg.ai",
    ) -> str:
        """
        Generate PIX EMV code (copia-e-cola).

        Based on BACEN specification for PIX QR Code.
        """
        # Simplified PIX code generation
        # In production, use a proper PIX library

        # Format amount (R$ 29.90 = "29.90")
        amount = f"{amount_cents / 100:.2f}"

        # PIX payload fields
        payload_format = "01"  # Payload Format Indicator
        merchant_account = f"0014BR.GOV.BCB.PIX01{len(self.PIX_KEY):02d}{self.PIX_KEY}"
        merchant_category = "0000"  # MCC
        currency = "986"  # BRL
        country = "BR"

        # Build EMV payload
        def field(id: str, value: str) -> str:
            return f"{id}{len(value):02d}{value}"

        emv = ""
        emv += field("00", payload_format)
        emv += field("26", merchant_account)
        emv += field("52", merchant_category)
        emv += field("53", currency)
        emv += field("54", amount)
        emv += field("58", country)
        emv += field("59", self.BENEFICIARY_NAME[:25])
        emv += field("60", self.BENEFICIARY_CITY[:15])
        emv += field("62", field("05", transaction_id[:25]))

        # CRC16 placeholder
        emv += "6304"

        # Calculate CRC16-CCITT
        crc = self._crc16_ccitt(emv.encode())
        emv = emv[:-4] + f"6304{crc:04X}"

        return emv

    def _crc16_ccitt(self, data: bytes) -> int:
        """Calculate CRC16-CCITT for PIX."""
        crc = 0xFFFF
        polynomial = 0x1021

        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ polynomial
                else:
                    crc <<= 1
                crc &= 0xFFFF

        return crc

    async def create_pix_order(
        self,
        db: Session,
        user: User,
        package_id: str,
    ) -> Dict[str, Any]:
        """
        Create a PIX payment order.

        Returns PIX code and instructions to send receipt via WhatsApp.
        """
        package = CREDIT_PACKAGES.get(package_id)
        if not package:
            raise ValueError(f"Invalid package: {package_id}")

        total_credits = calculate_package_credits(package)

        # Create transaction
        transaction = PixTransaction(
            user_id=user.id,
            amount_cents=package.price_cents,
            credits=total_credits,
            package_id=package_id,
            pix_key=self.PIX_KEY,
            status="pending",
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db.add(transaction)
        db.flush()

        # Generate PIX code
        pix_code = self.generate_pix_code(
            amount_cents=package.price_cents,
            transaction_id=transaction.id[:8].upper(),
            description=f"Creditos exeg.ai - {package.name}",
        )
        transaction.pix_code = pix_code

        # Generate QR Code (base64)
        qr_base64 = self._generate_qr_base64(pix_code)
        transaction.qr_code_base64 = qr_base64

        transaction.status = "awaiting_receipt"
        db.commit()

        # WhatsApp message template
        whatsapp_message = self.WHATSAPP_MESSAGE_TEMPLATE.format(
            transaction_id=transaction.id[:8].upper(),
            amount=format_price(package.price_cents),
            credits=f"{total_credits:,}".replace(",", "."),
            user_email=user.email,
        )

        return {
            "transaction_id": transaction.id,
            "status": transaction.status,
            "amount_cents": package.price_cents,
            "amount_formatted": format_price(package.price_cents),
            "credits": total_credits,
            "package": {
                "id": package.id,
                "name": package.name,
            },
            "pix": {
                "key": self.PIX_KEY,
                "key_type": self.PIX_KEY_TYPE,
                "beneficiary": self.BENEFICIARY_NAME,
                "code": pix_code,
                "qr_code_base64": qr_base64,
            },
            "whatsapp": {
                "number": self._whatsapp_number,
                "link": f"https://wa.me/{self._whatsapp_number.replace('+', '')}?text={self._url_encode(whatsapp_message)}",
                "message": whatsapp_message,
            },
            "instructions": [
                "1. Copie o código PIX ou escaneie o QR Code",
                "2. Faça o pagamento no seu banco",
                "3. Envie o comprovante pelo WhatsApp da Otimiza",
                "4. A ANA validará automaticamente e carregará seus créditos",
            ],
            "expires_at": transaction.expires_at.isoformat(),
        }

    def _generate_qr_base64(self, data: str) -> str:
        """
        Generate QR Code as base64.

        Uses a simple placeholder - in production use qrcode library.
        """
        try:
            import qrcode
            import io

            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode()
        except ImportError:
            # Fallback: return placeholder
            return ""

    def _url_encode(self, text: str) -> str:
        """URL encode text for WhatsApp link."""
        import urllib.parse
        return urllib.parse.quote(text)

    async def get_transaction_status(
        self,
        db: Session,
        user_id: str,
        transaction_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get status of a PIX transaction."""
        transaction = db.query(PixTransaction).filter(
            PixTransaction.id == transaction_id,
            PixTransaction.user_id == user_id,
        ).first()

        if not transaction:
            return None

        return {
            "transaction_id": transaction.id,
            "status": transaction.status,
            "amount_formatted": format_price(transaction.amount_cents),
            "credits": transaction.credits,
            "created_at": transaction.created_at.isoformat(),
            "expires_at": transaction.expires_at.isoformat() if transaction.expires_at else None,
            "confirmed_at": transaction.confirmed_at.isoformat() if transaction.confirmed_at else None,
            "validated_by": transaction.validated_by,
        }

    async def list_user_transactions(
        self,
        db: Session,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List user's PIX transactions."""
        transactions = db.query(PixTransaction).filter(
            PixTransaction.user_id == user_id
        ).order_by(
            PixTransaction.created_at.desc()
        ).offset(offset).limit(limit).all()

        return [
            {
                "transaction_id": t.id,
                "status": t.status,
                "amount_formatted": format_price(t.amount_cents),
                "credits": t.credits,
                "package_id": t.package_id,
                "created_at": t.created_at.isoformat(),
                "confirmed_at": t.confirmed_at.isoformat() if t.confirmed_at else None,
            }
            for t in transactions
        ]

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        """Verify webhook signature from Otimiza/ANA."""
        if not self._webhook_secret:
            return False

        expected = hmac.new(
            self._webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    async def confirm_payment(
        self,
        db: Session,
        transaction_id: str,
        bank_transaction_id: str,
        validated_by: str = "ana_ai",
        notes: str = None,
    ) -> Dict[str, Any]:
        """
        Confirm PIX payment after validation by ANA.

        Called by webhook from Otimiza Pagamentos.
        """
        transaction = db.query(PixTransaction).filter(
            PixTransaction.id == transaction_id
        ).first()

        if not transaction:
            raise ValueError(f"Transaction not found: {transaction_id}")

        if transaction.status == "confirmed":
            return {"already_confirmed": True, "transaction_id": transaction_id}

        if transaction.status == "rejected":
            raise ValueError("Transaction was rejected")

        if transaction.status == "expired":
            raise ValueError("Transaction expired")

        # Update transaction
        transaction.status = "confirmed"
        transaction.bank_transaction_id = bank_transaction_id
        transaction.validated_by = validated_by
        transaction.validation_notes = notes
        transaction.confirmed_at = datetime.utcnow()

        # Add credits to user
        credit_service.add_credits(
            db,
            transaction.user_id,
            transaction.credits,
            transaction_type="pix_purchase",
            description=f"PIX {transaction.package_id}: {transaction.credits:,} créditos".replace(",", "."),
        )

        db.commit()

        return {
            "success": True,
            "transaction_id": transaction_id,
            "credits_added": transaction.credits,
            "user_id": transaction.user_id,
        }

    async def reject_payment(
        self,
        db: Session,
        transaction_id: str,
        reason: str,
        validated_by: str = "ana_ai",
    ) -> Dict[str, Any]:
        """
        Reject PIX payment after validation by ANA.

        Called by webhook from Otimiza Pagamentos.
        """
        transaction = db.query(PixTransaction).filter(
            PixTransaction.id == transaction_id
        ).first()

        if not transaction:
            raise ValueError(f"Transaction not found: {transaction_id}")

        if transaction.status == "confirmed":
            raise ValueError("Cannot reject confirmed transaction")

        transaction.status = "rejected"
        transaction.validated_by = validated_by
        transaction.validation_notes = reason

        db.commit()

        return {
            "success": True,
            "transaction_id": transaction_id,
            "status": "rejected",
            "reason": reason,
        }

    async def expire_pending_transactions(self, db: Session) -> int:
        """Expire transactions older than 24 hours."""
        expired = db.query(PixTransaction).filter(
            PixTransaction.status.in_(["pending", "awaiting_receipt"]),
            PixTransaction.expires_at < datetime.utcnow(),
        ).all()

        count = 0
        for transaction in expired:
            transaction.status = "expired"
            count += 1

        if count > 0:
            db.commit()

        return count


# Singleton instance
pix_service = PixService()
