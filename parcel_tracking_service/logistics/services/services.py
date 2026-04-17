import uuid


def generate_tracking_number():
    return uuid.uuid4().hex[:12].upper()
