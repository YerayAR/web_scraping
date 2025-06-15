import tkinter as tk
from tkinter import messagebox # Added for main's error display
import time # For Xvfb startup delay if used
import os # For Xvfb and DISPLAY handling

# Use a try-except block for gui import
try:
    from gui import JobScraperApp
    from scraper import initialize_driver
except ImportError as e:
    print(f"Error importing modules for main.py (attempt 1): {e}")
    # Fallback for environments where job_scraper_project is the CWD
    try:
        from job_scraper_project.gui import JobScraperApp
        from job_scraper_project.scraper import initialize_driver
    except ImportError as e2:
        print(f"Error importing modules for main.py (attempt 2): {e2}. Ensure script is run from parent of job_scraper_project or job_scraper_project is in PYTHONPATH.")
        raise # Re-raise the exception to make it clear that imports failed


def main():
    driver = None  # Initialize driver to None
    # Check for DISPLAY environment variable for Tkinter, especially in headless environments
    if not os.environ.get('DISPLAY'):
        print("ADVERTENCIA: La variable de entorno DISPLAY no está configurada.")
        print("Si está en un entorno sin cabeza, la GUI puede fallar al iniciarse sin un servidor X virtual como Xvfb.")
        # Attempt to start Xvfb if it seems like a headless environment (very basic check)
        # In a real app, this would be handled by startup scripts or container config.
        if not os.environ.get("STY"): # STY is often set in terminal sessions, not in cron/headless
            print("Parece un entorno sin cabeza, intentando iniciar Xvfb...")
            if os.system("pgrep Xvfb > /dev/null") != 0:
                print("Iniciando Xvfb...")
                os.system("Xvfb :99 -screen 0 1280x1024x24 &")
                time.sleep(2) # Give Xvfb a moment to start
            os.environ['DISPLAY'] = ':99'
            print(f"DISPLAY configurado a: {os.environ.get('DISPLAY')}")


    try:
        print("Inicializando WebDriver...")
        driver = initialize_driver()

        if driver:
            print("WebDriver inicializado con éxito.")
            root = tk.Tk()
            app = JobScraperApp(root, driver)
            root.mainloop()
        else:
            print("Fallo al inicializar WebDriver. La aplicación no puede iniciar la GUI.")
            try:
                root_err = tk.Tk()
                root_err.withdraw()
                messagebox.showerror("Error Crítico", "Fallo al inicializar WebDriver. La aplicación no puede iniciar.")
                root_err.destroy()
            except tk.TclError:
                print("Tkinter no está disponible para mostrar el mensaje de error.")

    except tk.TclError as tcl_e:
        print(f"Error de Tkinter: {tcl_e}. Esto usualmente significa que no hay un servidor de visualización (DISPLAY) disponible.")
        print("Si está ejecutando esto en un servidor o un entorno sin cabeza, necesita Xvfb o una configuración similar.")
        # No more GUI error messages if Tkinter itself is the problem
    except Exception as e:
        print(f"Ocurrió un error inesperado en la aplicación: {e}")
        try:
            root_err = tk.Tk()
            root_err.withdraw()
            messagebox.showerror("Error Inesperado", f"Ocurrió un error inesperado: {e}")
            root_err.destroy()
        except tk.TclError:
            print("Tkinter no está disponible para mostrar el mensaje de error inesperado.")
    finally:
        # on_closing in JobScraperApp handles driver.quit() when GUI closes normally.
        # This finally block is a fallback if GUI didn't start or crashed before on_closing.
        if driver:
            try:
                # Check if driver session is still active. Accessing window_handles will error if quit.
                _ = driver.window_handles
                print("WebDriver todavía está activo después de que mainloop terminó o falló. Cerrando ahora.")
                driver.quit()
            except Exception:
                # This means driver was already closed or failed to initialize properly.
                print("WebDriver ya parece estar cerrado o no se inicializó completamente.")
        print("Aplicación finalizada.")

if __name__ == '__main__':
    main()
