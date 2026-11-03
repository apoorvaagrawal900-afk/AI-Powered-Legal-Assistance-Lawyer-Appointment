from app import generate_legal_help_reply

try:
    reply = generate_legal_help_reply(
        messages=[],
        question=(
            "My landlord is not returning my security deposit. "
            "The rented property is in Gwalior, Madhya Pradesh. "
            "What should I do?"
        )
    )

    print("Legal Help test successful")
    print(reply.model_dump_json(indent=2))

except Exception as exc:
    print(f"Error type: {type(exc).__name__}")
    print(f"Error details: {exc}")