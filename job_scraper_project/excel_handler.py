"""Utility for exporting scraped job entries to Excel files.

This module uses :mod:`pandas` to create a DataFrame from the list of
scraped job dictionaries and persists it to an ``.xlsx`` file.  It is
kept separate from the scraping logic so the data layer can be tested
independently of any web dependencies.
"""

import pandas as pd

def save_jobs_to_excel(all_jobs_data, filename="job_listings.xlsx"):
    """Persist the scraped job information to an Excel spreadsheet.

    Parameters
    ----------
    all_jobs_data : list of dict
        Collection of job entries produced by the scraping functions.  Each
        dictionary should contain keys such as ``Designación`` and
        ``Nombre de la empresa``.
    filename : str, optional
        Desired output filename.  Defaults to ``job_listings.xlsx``.
    """
    if not all_jobs_data:
        print("No job data to save.")
        return False

    try:
        # Convert list of dictionaries to a DataFrame so it can easily be
        # manipulated and exported by ``pandas``
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
                # Create empty columns for any missing fields to keep a
                # consistent Excel structure even when some data points are
                # not scraped
                df[col] = ""

        # Add "Número Sr" column (1-based index)
        # Insert a running index column so Excel has a simple serial number
        df.insert(0, "Número Sr", range(1, len(df) + 1))

        # Reorder DataFrame to match specified headers exactly, including "Número Sr"
        final_columns_order = [
            "Número Sr",
            "Designación",
            "Nombre de la empresa",
            "Ciudad",
            "Email",
            "Teléfono",
            "URL de la oferta",
        ]
        # Reorder DataFrame explicitly so the Excel output columns are
        # predictable regardless of the order in which fields were scraped
        df = df[final_columns_order]

        # Use openpyxl engine for Excel output since it supports modern xlsx
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Data successfully saved to {filename}")
        return True

    except Exception as e:
        # Any failure at this point is logged and ``False`` returned so the
        # calling GUI can react appropriately (e.g. show an error dialog)
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
