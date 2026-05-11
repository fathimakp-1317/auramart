import stripe
import os
from dotenv import load_dotenv

load_dotenv()

# initialize stripe with your secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def create_payment_intent(amount: float,
                           currency: str = "usd",
                           order_id: str = None) -> dict:
    """
    Create a Stripe Payment Intent.

    This tells Stripe we want to charge a customer.
    Frontend uses the client_secret to collect card details.

    amount   = total in dollars e.g. 59.98
    currency = "usd" by default
    order_id = our internal order ID for reference
    """
    # Stripe works in cents not dollars
    # so multiply by 100
    amount_in_cents = int(amount * 100)

    intent = stripe.PaymentIntent.create(
        amount=amount_in_cents,
        currency=currency,
        metadata={
            "order_id": order_id
            # metadata lets us find this payment later
        }
    )

    return {
        "payment_intent_id": intent.id,
        "client_secret":     intent.client_secret,
        # client_secret goes to frontend
        # frontend uses it to confirm payment
        "amount":            amount,
        "currency":          currency,
        "status":            intent.status
    }


def confirm_payment_intent(payment_intent_id: str) -> dict:
    """
    Retrieve and check status of a payment intent.
    Called after frontend confirms payment.
    """
    intent = stripe.PaymentIntent.retrieve(
        payment_intent_id
    )

    return {
        "payment_intent_id": intent.id,
        "status":            intent.status,
        "amount":            intent.amount / 100,
        "currency":          intent.currency
    }


def create_refund(payment_intent_id: str,
                  amount: float = None) -> dict:
    """
    Refund a payment.
    If amount is None, full refund is issued.
    """
    refund_data = {
        "payment_intent": payment_intent_id
    }

    if amount:
        refund_data["amount"] = int(amount * 100)

    refund = stripe.Refund.create(**refund_data)

    return {
        "refund_id": refund.id,
        "status":    refund.status,
        "amount":    refund.amount / 100
    }