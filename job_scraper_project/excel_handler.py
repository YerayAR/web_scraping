import pandas as pd

def save_jobs_to_excel(all_jobs_data, filename="job_listings.xlsx"):
    """
    Saves a list of job data (list of dictionaries) to an Excel file.

    Args:
        all_jobs_data (list): A list of dictionaries, where each dictionary
                              represents a job and contains keys like 'Designación',
                              'Nombre de la empresa', etc.
        filename (str): The name of the Excel file to save.
    """
    if not all_jobs_data:
        print("No job data to save.")
        return False

    try:
        df = pd.DataFrame(all_jobs_data)

        # Define the required columns in order
        required_columns = [
            "Designación",
            "Nombre de la empresa",
            "Ciudad",
            "Email",
            "Teléfono",
            "URL de la oferta"
        ]

        # Ensure all required columns exist, fill with default if not present in source
        # (though scraper should provide them, even if empty for Email/Teléfono)
        for col in required_columns:
            if col not in df.columns:
                df[col] = "" # Or pd.NA or None, depending on desired Excel output for missing

        # Add "Número Sr" column (1-based index)
        df.insert(0, "Número Sr", range(1, len(df) + 1))

        # Reorder DataFrame to match specified headers exactly, including "Número Sr"
        final_columns_order = [
            "Número Sr",
            "Designación",
            "Nombre de la empresa",
            "Ciudad",
            "Email",
            "Teléfono",
            "URL de la oferta"
        ]
        df = df[final_columns_order]

        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Data successfully saved to {filename}")
        return True

    except Exception as e:
        print(f"Error saving data to Excel: {e}")
        return False

if __name__ == '__main__':
    # Example Usage for testing excel_handler.py directly
    print("Testing excel_handler.py...")
    sample_jobs = [
        {
            "Designación": "Software Engineer",
            "Nombre de la empresa": "Tech Co",
            "Ciudad": "San Francisco",
            "Email": "hr@tech.co",
            "Teléfono": "123-456-7890",
            "URL de la oferta": "http://example.com/job/1"
        },
        {
            "Designación": "Data Analyst",
            "Nombre de la empresa": "Analytics R Us",
            "Ciudad": "New York",
            "Email": "", # Missing email
            "Teléfono": "", # Missing phone
            "URL de la oferta": "http://example.com/job/2"
        },
        { # Data that might be missing a standard column, to test robustness
            "Designación": "Project Manager",
            "Nombre de la empresa": "Org Solutions",
            # "Ciudad": "Chicago", # Missing City for testing default column creation
            "URL de la oferta": "http://example.com/job/3"
        }
    ]

    # Test with data
    save_jobs_to_excel(sample_jobs, "test_jobs_output.xlsx")

    # Test with empty data
    print("\nTesting with no data...")
    save_jobs_to_excel([], "test_empty_output.xlsx")

    # Test with slightly different keys (should still work if columns are created)
    sample_jobs_alt_keys = [
         {
            "Job Title": "UX Designer", # Different key name
            "Company": "DesignHub",
            "Location": "Remote",
            "Link": "http://example.com/job/4"
            # This won't map directly to "Designación", etc.
            # The current save_jobs_to_excel expects keys to match required_columns.
            # For this test to be meaningful for key mismatches, the DataFrame creation
            # would need more sophisticated mapping or renaming.
            # Let's stick to the defined structure for now.
            # The loop `for col in required_columns: if col not in df.columns: df[col] = ""`
            # handles missing columns, not differently named ones.
        }
    ]
    # To properly test mapping, we would need a transformation step before creating DataFrame
    # or pass data that already roughly conforms.
    # The current function will create empty columns for "Designación" etc. if sample_jobs_alt_keys is used.
    # This is acceptable.
    print("\nTesting with data that has some missing standard keys...")
    save_jobs_to_excel([
        {
            "Designación": "UX Designer",
            "Nombre de la empresa": "DesignHub",
            "URL de la oferta": "http://example.com/job/4"
            # City, Email, Teléfono are missing and should be added as empty
        }
    ], "test_missing_keys_output.xlsx")
