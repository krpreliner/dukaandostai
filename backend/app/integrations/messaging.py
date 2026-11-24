import httpx
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class MessagingIntegration:
    @classmethod
    def generate_campaign_draft(
        cls,
        campaign_name: str,
        target_segment: str,
        offer_description: str,
        discount_pct: float
    ) -> Dict[str, Any]:
        """
        Generates authentic bilingual promotional copy tailored to Kirana shoppers.
        """
        msg_en = (
            f"Namaste! Special offer from Sharma General Store, Ranchi: "
            f"Get {discount_pct:.1f}% off on {offer_description}. "
            f"Fresh stock, best wholesale rates. Visit us today at Harmu Road!"
        )
        msg_hi = (
            f"नमस्ते! शर्मा जनरल स्टोर, राँची की तरफ से विशेष ऑफर: "
            f"{offer_description} पर {discount_pct:.1f}% की विशेष छूट! "
            f"ताज़ा सामान और किफ़ायती दाम। आज ही पधारें!"
        )

        has_twilio = bool(getattr(settings, "TWILIO_ACCOUNT_SID", None) and getattr(settings, "TWILIO_AUTH_TOKEN", None))

        return {
            "campaign_name": campaign_name,
            "target_segment": target_segment,
            "status": "DRAFT",
            "is_live": False,
            "can_dispatch_live": has_twilio,
            "channel": "WhatsApp / SMS",
            "message_en": msg_en,
            "message_hi": msg_hi,
            "disclaimer": "Ready to dispatch. Enter Twilio API credentials in .env to transmit live WhatsApp or SMS messages." if not has_twilio else "Live dispatch enabled via Twilio."
        }

    @classmethod
    def send_live_message(
        cls,
        recipient_phone: str,
        message_body: str,
        channel: str = "sms"
    ) -> Dict[str, Any]:
        """
        Sends a REAL SMS or WhatsApp message using the configured Twilio API credentials.
        """
        account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", "").strip()
        auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", "").strip()
        from_phone = getattr(settings, "TWILIO_PHONE_NUMBER", "").strip()
        from_whatsapp = getattr(settings, "TWILIO_WHATSAPP_NUMBER", "").strip()

        if not account_sid or not auth_token:
            return {
                "success": False,
                "status": "CREDENTIALS_MISSING",
                "message": "Twilio Account SID or Auth Token is not configured. Please supply real API keys in .env or settings."
            }

        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

        # Format WhatsApp vs SMS sender & recipient
        if channel.lower() == "whatsapp":
            from_addr = f"whatsapp:{from_whatsapp}" if not from_whatsapp.startswith("whatsapp:") else from_whatsapp
            to_addr = f"whatsapp:{recipient_phone}" if not recipient_phone.startswith("whatsapp:") else recipient_phone
        else:
            from_addr = from_phone
            to_addr = recipient_phone

        data = {
            "From": from_addr,
            "To": to_addr,
            "Body": message_body
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, data=data, auth=(account_sid, auth_token))
                if res.status_code in [200, 201]:
                    tw_data = res.json()
                    return {
                        "success": True,
                        "status": "TRANSMITTED_LIVE",
                        "message_sid": tw_data.get("sid"),
                        "delivery_status": tw_data.get("status"),
                        "channel": channel.upper(),
                        "recipient": recipient_phone,
                        "details": f"Message successfully dispatched via Twilio network (SID: {tw_data.get('sid')})."
                    }
                else:
                    err = res.json().get("message", res.text)
                    return {
                        "success": False,
                        "status": "DISPATCH_FAILED",
                        "message": f"Twilio API Error ({res.status_code}): {err}"
                    }
        except Exception as e:
            logger.error(f"Failed to send live message: {e}")
            return {
                "success": False,
                "status": "NETWORK_ERROR",
                "message": f"Network error during Twilio dispatch: {str(e)}"
            }
