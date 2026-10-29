def validate_crop_input(data):
    errors = []

    # Location
    if not data.get("location"):
        errors.append("Location is required")

    # NPK validation
    for field in ["N", "P", "K"]:
        value = data.get(field)

        if value is None:
            continue  # allow default

        if not isinstance(value, (int, float)):
            errors.append(f"{field} must be a number")
        elif value < 0 or value > 150:
            errors.append(f"{field} must be between 0 and 150")

    # pH validation
    ph = data.get("ph")
    if ph is not None:
        if not isinstance(ph, (int, float)):
            errors.append("pH must be a number")
        elif ph < 0 or ph > 14:
            errors.append("pH must be between 0 and 14")

    return errors