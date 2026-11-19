import pandas as pd


def preprocess_transaction(
    transaction,
    encoder,
    model_features
):
    input_df = pd.DataFrame([transaction])

    categorical_columns = [
        "age",
        "gender",
        "merchant",
        "category"
    ]

    encoded_array = encoder.transform(
        input_df[categorical_columns]
    )

    encoded_df = pd.DataFrame(
        encoded_array,
        columns=encoder.get_feature_names_out()
    )

    result = pd.concat(
        [
            input_df[["step", "amount"]].reset_index(drop=True),
            encoded_df.reset_index(drop=True)
        ],
        axis=1
    )

    result = result.reindex(columns=model_features)

    return result