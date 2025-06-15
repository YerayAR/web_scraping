import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from tkinter import messagebox # For error dialogs
import threading # To run scraping in a separate thread
import time # For timestamp in filename
from urllib.parse import quote_plus # For filename sanitization

# Assuming scraper and excel_handler are in the same directory or accessible via PYTHONPATH
try:
    from .scraper import (initialize_driver, scrape_linkedin_jobs,
                           scrape_indeed, scrape_internshala,
                           scrape_linkedin_posts)
    from .excel_handler import save_jobs_to_excel
except ImportError: # Fallback for running gui.py directly for testing (if tkinter worked)
    from scraper import (initialize_driver, scrape_linkedin_jobs,
                         scrape_indeed, scrape_internshala,
                         scrape_linkedin_posts)
    from excel_handler import save_jobs_to_excel


class JobScraperApp:
    def __init__(self, root, driver): # Accept driver instance
        self.root = root
        self.driver = driver # Store the driver
        root.title("Job Scraper Tool")
        root.geometry("550x350") # Slightly wider for messages

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=11)
        self.root.option_add("*Font", default_font)

        title_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
        status_font = tkFont.Font(family="Helvetica", size=10)
        button_font = tkFont.Font(family="Helvetica", size=12, weight="bold")

        main_frame = ttk.Frame(root, padding="20 20 20 20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        title_label = ttk.Label(main_frame, text="Job Search Filter", font=title_font)
        title_label.pack(pady=(0, 20))

        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=5)

        ttk.Label(form_frame, text="Designación:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.designation_entry = ttk.Entry(form_frame, width=45)
        self.designation_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.designation_entry.insert(0, "Software Engineer")

        ttk.Label(form_frame, text="Ciudad:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.city_entry = ttk.Entry(form_frame, width=45)
        self.city_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.city_entry.insert(0, "Remote")

        form_frame.columnconfigure(1, weight=1)

        self.search_button = ttk.Button(main_frame, text="Buscar", command=self.trigger_search_thread, style="Accent.TButton")
        self.search_button.pack(pady=20, ipadx=10, ipady=5)

        self.status_var = tk.StringVar()
        self.status_var.set("Ingrese los criterios y presione 'Buscar'.")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=500, font=status_font, justify=tk.CENTER)
        status_label.pack(pady=(10, 0), fill=tk.X)

        style = ttk.Style()
        style.configure("Accent.TButton", font=button_font) # Removed background/foreground for broader compatibility

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def trigger_search_thread(self):
        # Run the actual search in a separate thread to keep GUI responsive
        self.search_thread = threading.Thread(target=self.start_search, daemon=True)
        self.search_thread.start()

    def start_search(self):
        designation = self.designation_entry.get()
        city = self.city_entry.get()

        if not designation or not city:
            self.status_var.set("Error: Designación y Ciudad son campos requeridos.")
            messagebox.showerror("Error de Entrada", "Designación y Ciudad son campos requeridos.")
            return

        if not self.driver:
            self.status_var.set("Error: WebDriver no inicializado.")
            messagebox.showerror("Error del WebDriver", "El WebDriver no se pudo inicializar. La aplicación podría necesitar reiniciarse.")
            return

        self.search_button.config(state=tk.DISABLED)
        self.status_var.set(f"Buscando: {designation} en {city}...")
        all_jobs_data = []

        try:
            # LinkedIn Jobs
            self.status_var.set(f"Buscando en LinkedIn Jobs para {designation} en {city}...")
            linkedin_jobs = scrape_linkedin_jobs(self.driver, designation, city)
            all_jobs_data.extend(linkedin_jobs)
            self.status_var.set(f"LinkedIn Jobs: {len(linkedin_jobs)} encontrados. Buscando en Indeed...")

            # Indeed
            indeed_jobs = scrape_indeed(self.driver, designation, city)
            all_jobs_data.extend(indeed_jobs)
            self.status_var.set(f"Indeed: {len(indeed_jobs)} encontrados. Buscando en Internshala...")

            # Internshala
            internshala_jobs = scrape_internshala(self.driver, designation, city)
            all_jobs_data.extend(internshala_jobs)
            self.status_var.set(f"Internshala: {len(internshala_jobs)} encontrados. Buscando en LinkedIn Posts...")

            # LinkedIn Posts (Basic)
            linkedin_posts = scrape_linkedin_posts(self.driver, designation, city)
            all_jobs_data.extend(linkedin_posts)
            self.status_var.set(f"LinkedIn Posts: {len(linkedin_posts)} encontrados. Total: {len(all_jobs_data)}.")

            if all_jobs_data:
                self.status_var.set(f"Guardando {len(all_jobs_data)} ofertas en Excel...")

                # Generate filename with timestamp
                current_time_str = time.strftime("%Y%m%d-%H%M%S")
                safe_designation = quote_plus(designation.replace(" ", "_"))
                safe_city = quote_plus(city.replace(" ", "_"))
                filename = f"job_listings_{safe_designation}_{safe_city}_{current_time_str}.xlsx"

                if save_jobs_to_excel(all_jobs_data, filename):
                    self.status_var.set(f"¡Éxito! {len(all_jobs_data)} ofertas guardadas en '{filename}'.")
                    messagebox.showinfo("Éxito", f"{len(all_jobs_data)} ofertas guardadas en '{filename}'.")
                else:
                    self.status_var.set("Error al guardar el archivo Excel.")
                    messagebox.showerror("Error de Archivo", "No se pudo guardar el archivo Excel.")
            else:
                self.status_var.set("No se encontraron ofertas para los criterios dados.")
                messagebox.showinfo("Sin Resultados", "No se encontraron ofertas para los criterios especificados.")

        except Exception as e:
            self.status_var.set(f"Error durante el proceso de scraping: {e}")
            messagebox.showerror("Error de Scraping", f"Ocurrió un error: {e}")
        finally:
            self.search_button.config(state=tk.NORMAL)

    def on_closing(self):
        if messagebox.askokcancel("Salir", "¿Desea salir de la aplicación?"):
            if self.driver:
                print("Cerrando WebDriver...")
                try:
                    self.driver.quit()
                except Exception as e:
                    print(f"Error al cerrar WebDriver: {e}") # Log error if quit fails
            self.root.destroy()

if __name__ == '__main__':
    # This is primarily for testing the GUI layout if tkinter is available.
    # The main execution should be through main.py which handles driver initialization.
    print("Ejecutando gui.py directamente. WebDriver no será funcional aquí.")
    print("Para la funcionalidad completa, ejecute main.py.")

    # Mock driver for layout testing if needed and if tkinter worked
    class MockDriver:
        def get(self, url): print(f"MockDriver: Navigating to {url}")
        def quit(self): print("MockDriver: Quitting")
        # Add other methods used by scrapers if direct testing of start_search was intended here

    root = tk.Tk()
    # app = JobScraperApp(root, MockDriver()) # Pass mock driver for layout test
    app = JobScraperApp(root, None) # Or pass None, start_search will show WebDriver error
    root.mainloop()
