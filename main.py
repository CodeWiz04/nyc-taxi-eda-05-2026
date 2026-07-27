"""

Entry point for the NYC Taxi EDA pipeline. Loads the cleaned dataset
(produced by src/data_cleaning.py), adds derived features, and runs
the full univariate + bivariate visualization suite, saving every
figure to images/.

"""

from src.utils import load_cleaned_data, add_derived_features, get_column_groups
from src.visualization import run_univariate_analysis, run_bivariate_analysis


def main():
    df = load_cleaned_data()
    df = add_derived_features(df)

    numerical_cols, low_cardinality_cats, high_cardinality_cols = get_column_groups(df)

    print("\nRunning univariate analysis...")
    run_univariate_analysis(df, numerical_cols, low_cardinality_cats, high_cardinality_cols)

    print("\nRunning bivariate analysis...")
    run_bivariate_analysis(df, numerical_cols)

    print("\nEDA complete. All figures saved to images/")


if __name__ == "__main__":
    main()