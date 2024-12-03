from rich import print as rprint

def print_status(message, status="info"):
    """
    Print pesan dengan warna sesuai status
    status: success (hijau), error (merah), info (cyan), warning (kuning)
    """
    status_styles = {
        "success": "bold green",
        "error": "bold red",
        "info": "bold cyan",
        "warning": "bold yellow"
    }
    style = status_styles.get(status, "white")
    rprint(f"[{style}]{message}[/{style}]") 
    
def logger(message, status="info"):
    """
    Print pesan dengan warna sesuai status
    status: success (hijau), error (merah), info (cyan), warning (kuning)
    """
    status_styles = {
        "success": "bold green",
        "error": "bold red",
        "info": "bold cyan",
        "warning": "bold yellow"
    }
    style = status_styles.get(status, "white")
    rprint(f"[{style}]{message}[/{style}]") 