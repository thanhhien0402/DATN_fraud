def predict_transaction(
    transaction,
    model,
    encoder,
    model_features,
    threshold
):
    from app.backend.preprocessing import preprocess_transaction

    X = preprocess_transaction(
        transaction,
        encoder,
        model_features
    )

    fraud_probability = float(
        model.predict_proba(X)[0][1]
    )

    predicted_label = int(
        fraud_probability >= threshold
    )

    return {
        "fraud_probability": fraud_probability,
        "predicted_label": predicted_label,
        "threshold": threshold
    }