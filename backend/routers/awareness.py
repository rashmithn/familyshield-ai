"""Curated, non-technical safety education content."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/awareness", tags=["awareness"])

AWARENESS_CONTENT: dict = {
    "categories": [
        {
            "id": "upi-scams",
            "title": "Common Indian UPI scams",
            "description": "How payment request fraud works.",
            "articles": [
                {
                    "id": "upi-collect-request",
                    "title": "Fake UPI collect request",
                    "summary": "A stranger asks you to approve a payment request you did not make.",
                    "content": [
                        "A collect request is a request to take money out of your account. A scammer may send one while pretending to refund you or deliver a parcel.",
                        "If you approve it, the money leaves your account immediately. A collect request can never be used to send money to you.",
                        "Open your payment app yourself to check any claim instead of tapping a link in a message.",
                    ],
                    "checklist": [
                        "Do not approve collect requests from people you do not know.",
                        "Check the amount and the name in your own payment app.",
                        "Report the request in the app and call your bank if money was taken.",
                    ],
                },
                {
                    "id": "upi-wrong-transfer",
                    "title": "Wrong transfer refund trick",
                    "summary": "Someone claims they sent you money by mistake and asks you to send it back.",
                    "content": [
                        "The caller may show a fake receipt and ask you to return the money to a different account.",
                        "Check your own bank or payment app statement before believing any screenshot.",
                        "If money really arrived, ask your bank how to return it safely.",
                    ],
                    "checklist": [
                        "Never refund to an account different from the one that paid you.",
                        "Do not scan a QR code sent by a stranger to 'collect a refund'.",
                    ],
                },
            ],
        },
        {
            "id": "otp-fraud",
            "title": "OTP and password fraud",
            "description": "Why one-time passwords must stay private.",
            "articles": [
                {
                    "id": "otp-sharing",
                    "title": "Never share your OTP",
                    "summary": "Bank staff never need your OTP, PIN or password.",
                    "content": [
                        "An OTP is the last lock on your account. Anyone who has it can move money or change your details.",
                        "Scammers often say there is a problem with your account and create urgency so you do not think clearly.",
                        "End the call and ring your bank on the number printed on your card or official website.",
                    ],
                    "checklist": [
                        "Do not read out or type an OTP for anyone.",
                        "Do not share screen during a banking call.",
                        "Tell a family member if someone asked you for an OTP.",
                    ],
                },
            ],
        },
        {
            "id": "fake-customer-care",
            "title": "Fake customer care numbers",
            "description": "How to find real support contacts.",
            "articles": [
                {
                    "id": "search-ad-helpline",
                    "title": "The helpline from a search result",
                    "summary": "Paid search results can show fake support numbers.",
                    "content": [
                        "A caller claiming to be from customer care may ask you to install a remote access app or share an OTP.",
                        "Real companies list their support numbers on their own website, app or product packaging.",
                        "Never allow a stranger to control your phone or computer.",
                    ],
                    "checklist": [
                        "Find support numbers on the official website, not from ads or messages.",
                        "Close the call if the person asks for a password, OTP or remote access.",
                    ],
                },
            ],
        },
        {
            "id": "digital-arrest",
            "title": "Digital arrest scams",
            "description": "No real police action happens over a video call.",
            "articles": [
                {
                    "id": "video-call-arrest",
                    "title": "You are not under digital arrest",
                    "summary": "A fake video call can claim you are being arrested unless you pay.",
                    "content": [
                        "Scammers may wear a police uniform, show a fake warrant and tell you not to disconnect or tell anyone.",
                        "There is no such thing as an online or digital arrest. Police do not demand money over a video call.",
                        "Disconnect the call and contact your local police station or a family member right away.",
                    ],
                    "checklist": [
                        "Disconnect any call that claims you are under digital arrest.",
                        "Do not transfer money or share your screen.",
                        "Call the national cybercrime helpline (1930 in India) if you paid.",
                    ],
                },
            ],
        },
        {
            "id": "fake-investments",
            "title": "Fake investments",
            "description": "Spot promised high returns before you lose money.",
            "articles": [
                {
                    "id": "guaranteed-returns",
                    "title": "Guaranteed high returns",
                    "summary": "Promises of quick, sure profits are a warning sign.",
                    "content": [
                        "Scammers may show fake profit screenshots and give small initial returns to build trust.",
                        "All investments carry risk. Nobody can guarantee large profits in a short time.",
                        "Check whether the adviser and product are registered with the regulator before investing.",
                    ],
                    "checklist": [
                        "Do not invest because of a message in a WhatsApp or Telegram group.",
                        "Never borrow money to chase guaranteed returns.",
                        "Discuss large decisions with a family member first.",
                    ],
                },
            ],
        },
        {
            "id": "social-engineering",
            "title": "Social engineering",
            "description": "How scammers use trust, fear and urgency.",
            "articles": [
                {
                    "id": "urgency-pressure",
                    "title": "Act now or lose your account",
                    "summary": "Pressure is a sign to slow down, not to hurry.",
                    "content": [
                        "Scammers say your account will close, a parcel is stuck or a prize will expire to make you act quickly.",
                        "They may also ask you to keep the conversation secret from family.",
                        "Legitimate organisations do not mind if you take time to check.",
                    ],
                    "checklist": [
                        "Pause and take three breaths before responding to urgent requests.",
                        "Verify using a phone number you already trust.",
                        "Ask another family member to look at the message.",
                    ],
                },
                {
                    "id": "impersonation",
                    "title": "Someone pretending to be someone else",
                    "summary": "A familiar name or photo can be copied.",
                    "content": [
                        "A message may claim to be from a friend, a bank officer or a government official.",
                        "Caller ID and profile pictures can be faked.",
                        "Confirm through a separate call to the person or organisation you know.",
                    ],
                    "checklist": [
                        "Do not send money because of a message alone.",
                        "Ask a question only the real person would know.",
                    ],
                },
            ],
        },
        {
            "id": "parent-safety-checklist",
            "title": "Safety checklist for parents and older adults",
            "description": "Simple habits that stop most scams.",
            "articles": [
                {
                    "id": "family-safety-habits",
                    "title": "Seven everyday safety habits",
                    "summary": "A short routine the whole family can remember.",
                    "content": [
                        "Keep your phone locked and never install apps from links in messages.",
                        "Use a different, long password for your bank and email accounts.",
                        "Decide as a family that no one will ever share an OTP or PIN, even with a person claiming to be staff.",
                        "If you lose money, call your bank immediately and dial 1930, the national cybercrime helpline in India.",
                    ],
                    "checklist": [
                        "Never share OTP, PIN, CVV or passwords.",
                        "Check unexpected payment requests inside your own app.",
                        "Verify officials using numbers from official websites.",
                        "Tell a family member about any suspicious message.",
                        "Do not pay advance fees for prizes or jobs.",
                        "Keep bank alerts switched on.",
                        "Report fraud quickly to your bank and the cybercrime helpline.",
                    ],
                },
            ],
        },
    ]
}


@router.get("")
def get_awareness() -> dict:
    return AWARENESS_CONTENT
