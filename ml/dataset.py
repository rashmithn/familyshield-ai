"""SYNTHETIC training dataset — invented examples only.

NOTHING in this file comes from real users, real messages or real scams.
All names, banks, amounts, links and phone numbers are fictional. The dataset
exists to teach a small text classifier the *shape* of suspicious language;
it is not evidence of real-world accuracy.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Example:
    text: str
    label: str       # "scam" or "safe"
    category: str


def _scam(category: str, *texts: str) -> list[Example]:
    return [Example(text, "scam", category) for text in texts]


def _safe(*texts: str) -> list[Example]:
    return [Example(text, "safe", "safe") for text in texts]


SYNTHETIC_EXAMPLES: list[Example] = []

SYNTHETIC_EXAMPLES += _scam(
    "fake_bank",
    "URGENT from SBI: your account will be blocked today. Update your KYC using the link to avoid suspension.",
    "HDFC alert: your debit card has been suspended. Verify your details immediately to restore service.",
    "ICICI Bank: unusual activity detected. Confirm your netbanking password within 30 minutes or account closure.",
    "State Bank notice: your account is deactivated due to pending KYC. Contact our manager on this number.",
    "Axis Bank: your credit card will expire tomorrow. Share your card number to reissue it immediately.",
    "Dear customer, your bank account has been blocked for security reasons. Call our helpline to unblock now.",
    "PNB fraud alert: your netbanking session will expire. Login here to verify your identity right now.",
    "Kotak Bank: we noticed suspicious transactions. Confirm your ATM PIN urgently to avoid a penalty.",
    "Your Bank of Baroda savings account needs immediate verification. Click here before end of day.",
    "RBI directive: all bank accounts without KYC update will be frozen. Verify using the attached link today.",
    "HDFC: your account will be debited for annual fee unless you verify your password immediately.",
    "SBI customer care says your account is under review. Share your internet banking password to keep it active.",
)

SYNTHETIC_EXAMPLES += _scam(
    "otp_request",
    "I am from the bank fraud team. Share the OTP you just received so we can stop the transaction.",
    "Your OTP is 482913. Please read it out to me to confirm your account and avoid blockage.",
    "Urgent: we need the one time password sent to your phone to complete your refund immediately.",
    "Send me the OTP now or your account will be permanently suspended. Do not tell anyone else.",
    "The delivery agent needs your OTP to hand over the parcel. Share it within 5 minutes.",
    "To process your prize money, provide the OTP and your ATM PIN to our executive on call.",
    "Customer care executive here: type the OTP in this chat to verify your identity right away.",
    "Never mind the earlier message, just tell me the six digit code that arrived on your mobile.",
    "Your UPI payment is stuck. Enter the OTP and password below to release the money immediately.",
    "This is the tax department. Share the OTP to avoid legal action and a fine by tonight.",
    "I am the bank manager. Give me your passcode over the call so I can update your KYC.",
    "We have sent a code to your number. Read it back to us to claim your cashback offer.",
)

SYNTHETIC_EXAMPLES += _scam(
    "upi_payment_scam",
    "You have received a UPI collect request of Rs 5000. Approve it now to get your refund.",
    "Your Paytm wallet needs verification. Approve the pending payment request to keep your account active.",
    "PhonePe collect request pending: pay Rs 1999 to confirm your cashback offer before it expires.",
    "I have sent you money by mistake on UPI. Please return it to rahul@fakeupi immediately.",
    "Google Pay reward of Rs 5000 is waiting. Approve the collect request to claim your reward.",
    "UPI request failed. Send Rs 10 verification payment to verify your account and receive the refund.",
    "A collect request from an unknown merchant is pending. Approve within 10 minutes or lose the parcel.",
    "Your bank will reverse the amount only after you approve the UPI request for processing fee.",
    "Scan this UPI QR code to receive your pending payment of Rs 25000. Do not share this with anyone.",
    "Your UPI limit will be blocked. Pay a small verification amount to the given handle to continue.",
    "Collect request from anna@paytm for Rs 4500. Approve now to complete your job registration.",
    "The refund is on hold. Approve the UPI request and we will credit double the amount to your account.",
)

SYNTHETIC_EXAMPLES += _scam(
    "lottery",
    "Congratulations! You have won a lottery of Rs 25 lakh. Pay Rs 5000 processing fee to claim your prize.",
    "You are the lucky winner of a cash prize. Share your bank details and deposit tax to receive the money.",
    "Your number was selected in a lucky draw. Claim your reward today by paying a small processing charge.",
    "You have won the jackpot. Send Rs 999 as tax before we transfer your prize amount.",
    "Festival lottery result: you won Rs 10 lakh. Contact our executive and pay the release fee immediately.",
    "Claim your prize of Rs 1 crore now. Bank details and an advance fee are required today only.",
    "Your reward is ready. Pay the customs duty on the prize money to receive it within 24 hours.",
    "Lucky draw winner! Transfer a nominal fee to confirm your identity and claim the cash prize.",
    "You won a government lottery. Pay the mandatory tax first or the prize will be cancelled.",
    "Congratulations, your reward of Rs 50000 is approved. Share your card details for verification.",
    "Free gift offer selected for you. Pay the delivery charge now to claim your lucky prize.",
    "Jackpot alert: claim your lottery money by paying a processing fee to our agent immediately.",
)

SYNTHETIC_EXAMPLES += _scam(
    "fake_job_offer",
    "Work from home job available. Earn Rs 30000 per day. Pay Rs 2000 registration fee to start.",
    "Hiring immediately for part time job. Send your bank details and a deposit for training materials.",
    "Job offer from a reputed company: earn a salary from home. Pay the security deposit today.",
    "Remote data entry vacancy. Stipend Rs 15000 per week. Contact us on WhatsApp and pay the joining fee.",
    "Great opportunity: earn easy money by rating products. Registration fee of Rs 999 is refundable.",
    "We are hiring freshers. SalaryRs 40000 per month. Pay the training fee to confirm your seat.",
    "Part time job for students. Work one hour daily and get paid. Send Rs 1500 for registration.",
    "Company hiring online supervisors. Deposit Rs 3000 to receive your official appointment letter.",
    "Earn Rs 500 per task from home. Join our Telegram group and pay the activation charge.",
    "Job vacancy with guaranteed salary. Share your bank details and pay processing fee immediately.",
    "Work from home offer: no experience needed. Pay for the starter kit and begin earning today.",
    "Vacancy for online assistant. Salary credited daily. Advance payment required for your ID card.",
)

SYNTHETIC_EXAMPLES += _scam(
    "investment_scam",
    "Invest Rs 10000 in our trading group and get guaranteed returns of 30 percent every month.",
    "Crypto investment opportunity with guaranteed profit. Join our Telegram group and transfer coins now.",
    "Double your money in 7 days with our verified stock tips. Limited slots available today.",
    "Mutual fund adviser here: guaranteed high returns if you invest before the market closes today.",
    "Forex trading bonus of Rs 50000 for new investors. Send the investment amount to our account.",
    "Put money in our bitcoin plan and receive a fixed profit every week with no risk at all.",
    "Join our exclusive investment group for high returns. Pay the membership fee to get started.",
    "We guarantee profit on every trade. Invest now and withdraw your earnings within 24 hours.",
    "Government approved investment scheme with assured returns. Transfer funds to the official account.",
    "Your friend suggested this investment app. It promises huge interest and a bonus for referrals.",
    "Stock market secret: invest a small amount and earn guaranteed profit daily. Call our adviser now.",
    "New investment plan offering 50 percent bonus on deposits. Only for the first hundred customers.",
)

SYNTHETIC_EXAMPLES += _scam(
    "delivery_scam",
    "Your parcel is held at customs. Pay Rs 350 clearing fee immediately to avoid destruction.",
    "Delivery failed. Reschedule your package by paying a small redelivery charge using this link.",
    "Courier update: your package is stuck. Confirm your address and pay the customs duty now.",
    "Your shipment cannot be delivered because of an unpaid fee. Click here to pay before today.",
    "A parcel with your name is at the warehouse. Pay the storage charge to release it immediately.",
    "Delivery partner here: your package needs an OTP to complete the delivery. Share it now.",
    "Your courier has been held for verification. Pay Rs 199 to avoid return to sender.",
    "Package delivery alert: your item is on hold due to unpaid customs duty. Settle it today.",
    "We could not deliver your parcel. Update your address and pay the rescheduling fee here.",
    "Shipment blocked by customs. Transfer the fee to the given account to receive your parcel.",
    "Your delivery is pending a verification fee. Pay immediately or the parcel will be destroyed.",
    "Courier company: your package contains restricted items. Pay the penalty to release it now.",
)

SYNTHETIC_EXAMPLES += _scam(
    "phishing",
    "Click here to verify your account or it will be permanently closed within 24 hours.",
    "We noticed unusual sign in. Visit this link and update your details immediately to stay safe.",
    "Your account needs identity confirmation. Open the link below and enter your password to continue.",
    "Please login here to confirm your identity and restore access to your account today.",
    "Security alert: verify your account now using the link in this message to avoid suspension.",
    "Update your details at this page within two hours or your profile will be deleted.",
    "Confirm your email and password here to receive your pending payment from the company.",
    "A document is waiting for you. Open the link and sign in with your bank credentials.",
    "Your subscription expired. Click here to update payment information and avoid a fine.",
    "Sign in through this secure link to check your refund status before the deadline.",
    "Click the link below and enter your card details to verify a suspicious transaction.",
    "Your account access is limited. Verify your identity here immediately to avoid closure.",
)

SYNTHETIC_EXAMPLES += _scam(
    "impersonation",
    "This is the income tax officer. You have a pending notice and must pay the fine today.",
    "I am the police inspector handling your case. Contact me immediately on this private number.",
    "RBI official here. Your bank account is being audited; share your details to avoid action.",
    "I am the manager from your bank's head office. Call me privately to resolve your account issue.",
    "This is the CBI. A case has been registered against you. Pay the penalty to avoid arrest.",
    "The electricity department executive says your connection will be cut. Pay the pending bill now.",
    "I am calling from the government helpline. Verify your identity to receive your subsidy.",
    "A senior officer from the tax department needs your bank details to process your refund.",
    "Your bank director has requested a confidential call. Do not tell anyone and call back now.",
    "I am from the consumer forum. Transfer the fee to file your complaint before the deadline.",
    "This is the customs department. Your package has documents; pay the penalty immediately.",
    "The registrar's office is contacting you about property papers. Pay the verification charge today.",
)

SYNTHETIC_EXAMPLES += _scam(
    "urgent_payment_request",
    "URGENT: transfer Rs 15000 to this account right now or your service will be disconnected.",
    "Pay immediately before 5 pm or a penalty will be added to your account. Do not delay.",
    "Last chance: send the payment today only, otherwise your application will be rejected.",
    "Act fast. The offer expires in 30 minutes and you will lose the entire refund amount.",
    "Your account will be blocked within 2 hours. Pay the pending amount using this number.",
    "Immediately transfer the verification amount to keep your order active. Time is running out.",
    "Do not wait. Send the money now and confirm with a screenshot to avoid cancellation.",
    "The deadline is today. Pay the outstanding fee now or face legal action tomorrow.",
    "Hurry, only a few slots remain. Pay the registration amount immediately to secure your place.",
    "Urgent request from your manager: buy gift cards and share the codes before the meeting.",
    "Your card will be charged a penalty unless you call and pay the outstanding amount immediately.",
    "Finish the payment within 10 minutes or your parcel will be returned to the sender.",
)

SYNTHETIC_EXAMPLES += _scam(
    "digital_arrest",
    "Digital arrest: you are under investigation. Stay on this video call until we finish checking.",
    "You are under arrest for money laundering. Do not disconnect the video call or tell your family.",
    "An arrest warrant has been issued against you. Pay the bail amount to avoid police action today.",
    "Police video call: you are being investigated. Keep this conversation secret and transfer funds.",
    "Do not disconnect this call. You are under digital arrest and cannot leave until cleared.",
    "We are from the cyber crime branch. You are under online arrest; move money to a safe account.",
    "A warrant is ready. Stay on the video call and follow our instructions or you will be jailed.",
    "You have been placed under digital arrest. Share your bank statements to prove your innocence.",
    "Federal officers are investigating you. Do not inform anyone and remain on the call.",
    "Your Aadhaar is linked to a crime. You are under arrest; pay the clearance fee immediately.",
    "Police have issued an online arrest notice. Transfer money for verification to avoid jail.",
    "Stay on the video call, do not tell your family, and transfer the amount as we instruct.",
)

SYNTHETIC_EXAMPLES += _scam(
    "fake_customer_care",
    "Call our customer care toll free number 1800 123 4567 to get your refund processed today.",
    "Customer service executive here. Install the remote support app so we can fix your bank account.",
    "Our helpline can reverse the charge. Call this number and share your card details for verification.",
    "Search result support team: contact us on WhatsApp to get immediate refund for your failed payment.",
    "Toll free 1800 987 6543. Our support team will connect to your screen to process the refund.",
    "Customer care has detected a problem with your order. Call us now and provide your OTP.",
    "Refund desk: we need remote access to your phone to complete the verification and release money.",
    "Technical support team from the app store says your account will be deleted. Call this number.",
    "Our service centre will refund you. Send Rs 1 to this account to activate the refund process.",
    "Support agent here: share the screen of your banking app so we can check the pending transaction.",
    "Customer care from your electricity provider: pay the pending amount to our executive on call.",
    "Helpline alert: your connection will be cut. Contact the given number and pay immediately.",
)

SYNTHETIC_EXAMPLES += _safe(
    "Hi Ravi, are we still meeting for lunch tomorrow near the office?",
    "The monthly family budget file has been updated in the shared folder.",
    "Your electricity bill for November is Rs 1840 and is due on the 12th of next month.",
    "Reminder: school parent teacher meeting is scheduled for Friday at 4 pm.",
    "I have booked the train tickets for our holiday. The departure time is 8:30 in the morning.",
    "Please pick up milk and bread on your way home this evening.",
    "The weather forecast says it may rain heavily in the city this weekend.",
    "Your appointment with the dentist has been confirmed for Tuesday morning.",
    "Thank you for the payment. Your invoice has been attached to the email as requested.",
    "The library will remain closed on Monday for maintenance work.",
    "Can you send me the recipe for the cake you made last week?",
    "We have scheduled the monthly family video call for Sunday at 7 pm.",
    "The flight was delayed by one hour, so I will reach the airport later than planned.",
    "Your order has been shipped and is expected to arrive on Thursday.",
    "The local community meeting will discuss the new park and its opening hours.",
    "Please review the attached meeting notes before our call tomorrow.",
    "I will bring the documents to the office when I come in this afternoon.",
    "The gym has extended its evening hours starting from next week.",
    "Happy birthday to our neighbour. The celebration is at 6 pm on Saturday.",
    "The bank statement for October is available in your online account.",
    "Could you please water the plants while we are away this weekend?",
    "Your appointment number is 42. Please wait in the reception area.",
    "The train platform has changed to number three because of scheduled work.",
    "We received your application and will respond within seven working days.",
    "The recipe uses two cups of flour, one cup of sugar and three eggs.",
    "Please let me know if you need a ride to the airport on Monday.",
    "The book club will discuss the novel we chose last month.",
    "Your subscription renews automatically unless you cancel it in the app.",
    "The office will be closed for the public holiday on Thursday.",
    "I enjoyed the photographs you shared from the family trip last week.",
    "The contractor will visit between 10 am and noon to check the water heater.",
    "Please confirm the time for dinner so I can make the reservations.",
    "The local bus service has added a new route through our neighbourhood.",
    "Your parcel was delivered this morning and signed for by a family member.",
    "The results of the school sports day have been published on the notice board.",
    "I have transferred your share of the grocery bill using the payment app.",
    "Please check the meeting room booking before you travel to the office.",
    "The museum is open from 10 am to 5 pm on weekdays.",
    "We should leave early to avoid the traffic near the bridge.",
    "The doctor advised rest for two days and a follow up visit next week.",
)

# Clearly synthetic URL strings, so the same model can inspect URL scans.
SYNTHETIC_EXAMPLES += _scam(
    "phishing",
    "http://192.168.1.50/verify-account?otp=123456",
    "https://sbi-bank-verify.info/login",
    "http://paytmm.cash/refund/claim",
    "https://hdfc-bank-update.top/kyc?pin=482913",
    "http://bit.ly/fake-prize-claim",
    "https://phonepee-secure.xyz/approve/collect",
    "http://103.24.55.11/reset/password",
    "https://amaz0n-deals.tk/account/verify",
    "http://icici-online.cc/secure/login?card=4111111111111111",
    "https://google-verify-account.ml/signin",
)

SYNTHETIC_EXAMPLES += _safe(
    "https://www.sbi.co.in/",
    "https://www.hdfcbank.com/",
    "https://www.icicibank.com/",
    "https://www.amazon.in/",
    "https://www.google.com/",
    "https://www.microsoft.com/en-in/",
    "https://www.phonepe.com/",
    "https://www.paytm.com/",
    "https://www.flipkart.com/",
    "https://example.com/blog/family-safety-tips",
)


def get_examples() -> list[Example]:
    """Return a copy of the synthetic dataset."""
    return list(SYNTHETIC_EXAMPLES)


CATEGORIES = sorted({example.category for example in SYNTHETIC_EXAMPLES})

if __name__ == "__main__":
    from collections import Counter

    print(f"Synthetic examples: {len(SYNTHETIC_EXAMPLES)}")
    for label, count in sorted(Counter(e.label for e in SYNTHETIC_EXAMPLES).items()):
        print(f"  {label}: {count}")
    for category, count in sorted(Counter(e.category for e in SYNTHETIC_EXAMPLES).items()):
        print(f"  {category}: {count}")
