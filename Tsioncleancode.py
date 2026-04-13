import pandas as pd

# Load dataset
df = pd.read_csv("U.S._Chronic_Disease_Indicators.csv")


# Remove columns with too many NaNs
threshold = len(df) * 0.5
df = df.dropna(axis=1, thresh=threshold)


# Drop unnecessary ID columns
cols_to_drop = [col for col in df.columns if "ID" in col]
df = df.drop(columns=cols_to_drop, errors='ignore')


# Drop rows missing key values
df = df.dropna(subset=['DataValue', 'YearStart', 'LocationDesc'])


# Fix data types
df['DataValue'] = pd.to_numeric(df['DataValue'], errors='coerce')
df['YearStart'] = pd.to_numeric(df['YearStart'], errors='coerce')


# Fill remaining missing values
if 'Stratification1' in df.columns:
    df['Stratification1'] = df['Stratification1'].fillna('Unknown')

if 'LowConfidenceLimit' in df.columns:
    df['LowConfidenceLimit'] = df['LowConfidenceLimit'].fillna(df['DataValue'])

if 'HighConfidenceLimit' in df.columns:
    df['HighConfidenceLimit'] = df['HighConfidenceLimit'].fillna(df['DataValue'])


# Keep only useful columns
columns_to_keep = [
    'YearStart',
    'YearEnd',
    'LocationDesc',
    'Topic',
    'Question',
    'DataValue',
    'DataValueType',   
    'LowConfidenceLimit',
    'HighConfidenceLimit',
    'Stratification1'
]
df_clean = df[[col for col in columns_to_keep if col in df.columns]]

# Clean text formatting
for col in ['LocationDesc', 'Topic', 'Question', 'Stratification1']:
    if col in df_clean.columns:
        df_clean[col] = df_clean[col].astype(str).str.strip()


# Remove duplicates
df_clean = df_clean.drop_duplicates()

# Optional: Sort data
df_clean = df_clean.sort_values(by=['YearStart', 'LocationDesc'])


# Save cleaned dataset
df_clean.to_csv("cleaned_chronic_disease_data.csv", index=False)


