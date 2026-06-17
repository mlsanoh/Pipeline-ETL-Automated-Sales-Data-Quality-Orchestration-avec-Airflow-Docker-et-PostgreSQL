from extract import extract_data_callable
from transform import transform_data_callable
from data_quality import data_quality_callable
from load import load_data_callable


def run_pipeline_test():

    print("START PIPELINE TEST")

    # 1. Extract
    df = extract_data_callable()
    print("✅ Extract OK :", df.shape)

    # 2. Transform
    df = transform_data_callable(df)
    print("✅ Transform OK :", df.shape)

    # 3. Data Quality
    df = data_quality_callable(df)
    print("✅ Data Quality OK :", df.shape)

    # 4. Load (optionnel pendant test)
    load_data_callable(df)
    print("✅ Load OK")

    print("PIPELINE COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    run_pipeline_test()