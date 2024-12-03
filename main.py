import requests
import json
import time
import re
from bs4 import BeautifulSoup
import random
import string
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text
from datetime import datetime, timedelta
from functools import partial
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from api.proxy_handler import ProxyHandler
from api.header import create_random_device_info, get_random_headers
from api.names import indonesian_names
from api.register import OasisRegister
from api.providers import create_providers as create_providers_util
from api.providers import run_providers as run_providers_util

def clear():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def key_bot():
    api = "https://itbaarts.com/api_prem.json"
    try:
        response = requests.get(api)
        response.raise_for_status()
        try:
            data = response.json()
            header = data['header']
            print('\033[96m' + header + '\033[0m')
        except json.JSONDecodeError:
            print('\033[96m' + response.text + '\033[0m')
    except requests.RequestException as e:
        print('\033[96m' + f"Failed to load header: {e}" + '\033[0m')

def create_styled_console():
    return Console(highlight=False)

def print_status(message, status="info"):
    status_styles = {
        "success": "bold green",
        "error": "bold red",
        "info": "bold cyan",
        "warning": "bold yellow"
    }
    style = status_styles.get(status, "white")
    rprint(f"[{style}]{message}[/{style}]")

def create_progress():
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        expand=False
    )

def print_progress(current, total):
    """Fungsi untuk menampilkan progress yang lebih sederhana"""
    percentage = (current / total) * 100
    print(f"\n[+] Progress: {current}/{total} ({percentage:.0f}%)")

def save_account(email, password, username_password):
    """Menyimpan akun ke file accounts.txt dan update referral count"""
    try:
        with open('accounts.txt', 'a') as f:
            f.write(f"{email}|{password}\n")
        print(f"[+] Akun berhasil disimpan ke accounts.txt")
        
        # Update referral count setelah berhasil menyimpan
        total_reff, max_reff = update_referral_count(username_password)
        if total_reff is not None:
            remaining = max_reff - total_reff
            print(f"[+] Sisa referral: {remaining}")
            
    except Exception as e:
        print(f"[-] Error saat menyimpan akun: {str(e)}")

def generate_password(email):
    """Generate password dari username email"""
    username = email.split('@')[0]
    # Kapitalisasi huruf pertama dan tambahkan @ di akhir
    return f"{username[0].upper()}{username[1:]}@"

def create_spinner():
    """Membuat spinner tanpa memerlukan deskripsi"""
    return Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[cyan]{task.description}"),
        transient=True,
        expand=False
    )

def get_passwords():
    """Mengambil daftar password dari server"""
    try:
        response = requests.get('https://airdrop.itbaarts.com/password.php')
        if response.ok:
            passwords = {}
            for line in response.text.strip().split():
                if '|' in line:
                    username, date = line.split('|')
                    passwords[username] = date
            return passwords
        return None
    except:
        return None

def verify_password():
    """Verifikasi password dan tanggal kadaluarsa"""
    console = create_styled_console()
    console.print("\n[bold cyan]VERIFIKASI PASSWORD[/bold cyan]")
    console.print("[cyan]─" * 30 + "[/cyan]\n")
    
    passwords = get_passwords()
    if not passwords:
        print_status("Gagal mengambil data password dari server", "error")
        return False, None
    
    username = console.input("[bold white]Username : [/bold white]").strip()
    
    if username not in passwords:
        print_status("Username tidak ditemukan", "error")
        return False, None
    
    # Cek tanggal kadaluarsa
    try:
        expire_date = datetime.strptime(passwords[username], "%d/%m/%Y").date()
        today = datetime.now().date()
        
        if today > expire_date:
            print_status(f"Password sudah kadaluarsa pada {passwords[username]}", "error")
            return False, None
            
        print_status("Verifikasi berhasil", "success")
        return True, username
        
    except ValueError:
        print_status("Format tanggal tidak valid", "error")
        return False, None

def get_max_referral(password):
    """Mengambil jumlah maksimal referral yang diizinkan"""
    try:
        response = requests.get(f'https://airdrop.itbaarts.com/max_ref.php?password={password}')
        if response.ok:
            data = response.text.strip().split('|')
            if len(data) == 2:
                total_reff = int(data[0])
                max_reff = int(data[1])
                return total_reff, max_reff
    except:
        pass
    return None, None

def update_referral_count(password):
    """Update jumlah referral setelah registrasi berhasil"""
    try:
        response = requests.get(f'https://airdrop.itbaarts.com/max_ref.php?password={password}&change_reff')
        if response.ok:
            data = response.text.strip().split('|')
            if len(data) == 2:
                total_reff, max_reff = int(data[0]), int(data[1])
                print(f"[+] Referral count diupdate: {total_reff}/{max_reff}")
                return total_reff, max_reff
    except Exception as e:
        print(f"[-] Gagal update referral count: {str(e)}")
    return None, None

class RateLimiter:
    def __init__(self, max_requests=10, time_window=1):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.lock = threading.Lock()

    def can_proceed(self):
        now = datetime.now()
        with self.lock:
            # Hapus request yang sudah lewat time window
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < timedelta(seconds=self.time_window)]
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False

    def wait_if_needed(self):
        while not self.can_proceed():
            time.sleep(0.1)

class ThreadSafeCounter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()
        
    def increment(self):
        with self.lock:
            self.count += 1
            return self.count
            
    def get_count(self):
        with self.lock:
            return self.count

def worker(task_queue, rate_limiter, counter, total_tasks, referral_code, progress_lock, username_password):
    while True:
        try:
            task_id = task_queue.get_nowait()
        except queue.Empty:
            break

        current = counter.increment()
        print(f"\n[+] Processing task {current}/{total_tasks}")
        
        rate_limiter.wait_if_needed()
        oasis = OasisRegister()
        
        for attempt in range(3):  # Max 3 attempts per task
            try:
                # Generate email
                email, username, domain = oasis.get_email()
                if not email:
                    print_status(f"Task {current}: Gagal generate email", "error")
                    continue
                    
                # Generate password
                password = generate_password(email)
                
                print_status(f"Task {current}: Email    : {email}", "info")
                print_status(f"Task {current}: Password : {password}", "info")
                
                # Register and verify
                if oasis.register_and_verify(email, password, referral_code):
                    save_account(email, password, username_password)
                    print_status(f"Task {current}: Account saved successfully", "success")
                    break
                else:
                    print_status(f"Task {current}: Registration or verification failed", "error")
                    time.sleep(random.uniform(1, 2))
                    
            except Exception as e:
                print_status(f"Error pada task {current}: {str(e)}", "error")
                if attempt < 2:
                    time.sleep(2)
                    
        task_queue.task_done()

def process_referrals_threaded(num_referrals, referral_code, username_password, max_threads=10):
    # Tingkatkan jumlah request per detik yang diizinkan
    rate_limiter = RateLimiter(max_requests=8, time_window=1)
    task_queue = queue.Queue()
    for i in range(num_referrals):
        task_queue.put(i)
        
    counter = ThreadSafeCounter()
    progress_lock = threading.Lock()
    
    threads = []
    num_threads = min(max_threads, num_referrals)
    
    print(f"[+] Memulai {num_threads} threads")
    
    for _ in range(num_threads):
        thread = threading.Thread(
            target=worker,
            args=(task_queue, rate_limiter, counter, num_referrals, referral_code, progress_lock, username_password)
        )
        thread.daemon = True  # Set thread sebagai daemon
        thread.start()
        threads.append(thread)
        # Tambahkan delay kecil antar pembuatan thread
        time.sleep(0.1)
        
    try:
        task_queue.join()
    except KeyboardInterrupt:
        print("\n[!] Menghentikan proses...")
        return
        
    for thread in threads:
        thread.join()
        
    print("\n[+] Semua tasks selesai")

async def create_providers(console, username, is_premium):
    """Fungsi untuk membuat providers"""
    console.print("\n[bold cyan]OASIS AI CREATE PROVIDERS[/bold cyan]")
    console.print("[cyan]─" * 30 + "[/cyan]\n")
    
    try:
        # Cek apakah file tokens.txt ada
        try:
            with open('tokens.txt', 'r') as f:
                tokens = f.read().strip().splitlines()
                if not tokens:
                    raise FileNotFoundError
        except FileNotFoundError:
            print_status("File tokens.txt tidak ditemukan atau kosong", "error")
            print_status("Silakan login terlebih dahulu untuk mendapatkan token", "info")
            return

        num_providers = int(console.input("[bold white]Jumlah providers per akun (1-5) : [/bold white]"))
        
        # Tambahkan pengecekan batasan provider berdasarkan username
        if username != "120698":  # Username khusus tanpa batasan
            if num_providers > 5:
                print_status("Maksimal 5 providers per akun untuk user biasa", "warning")
                num_providers = 5
        
        if num_providers < 1:
            print_status("Jumlah providers minimal 1", "error")
            return
            
        print_status("\nMemulai pembuatan providers...", "info")
        
        # Jalankan create_providers dari api.providers
        success = await create_providers_util(num_providers, is_premium)
        
        if success:
            print_status("\nPembuatan providers selesai", "success")
            print_status("Token providers tersimpan di providers.txt", "info")
            
            # Hapus akun dari accounts.txt setelah provider berhasil dibuat
            with open('accounts.txt', 'r') as f:
                accounts = f.readlines()
            with open('accounts.txt', 'w') as f:
                for account in accounts:
                    if username not in account:
                        f.write(account)
        else:
            print_status("\nGagal membuat providers", "error")
            
    except ValueError:
        print_status("Input tidak valid", "error")
    except Exception as e:
        print_status(f"Error: {str(e)}", "error")
    
    console.input("\n[bold white]Tekan Enter untuk kembali ke menu[/bold white]")

async def run_providers(console, username, is_premium):
    """Fungsi untuk menjalankan providers"""
    console.print("\n[bold cyan]OASIS AI RUN PROVIDERS[/bold cyan]")
    console.print("[cyan]─" * 30 + "[/cyan]\n")
    
    try:
        # Tanya apakah ingin menggunakan proxy
        use_proxy = 'y'
        
        # Jalankan run_providers dari api.providers
        run_providers_util(use_proxy, is_premium)
            
    except Exception as e:
        print_status(f"Error: {str(e)}", "error")
    
    console.input("\n[bold white]Tekan Enter untuk kembali ke menu[/bold white]")

async def main():
    clear()
    key_bot()
    
    console = create_styled_console()
    console.print("\n[bold cyan]PILIH TIPE USER[/bold cyan]")
    console.print("[cyan]─" * 30 + "[/cyan]\n")
    console.print("[1] Premium User")
    console.print("[2] Free User\n")
    
    user_type = console.input("[bold white]Pilih tipe user (1-2): [/bold white]")
    
    if user_type not in ["1", "2"]:
        console.print("\n[red]Pilihan tidak valid![/red]")
        return
        
    is_premium = user_type == "1"
    
    if is_premium:
        success, username = verify_password()
        if not success:
            return
    else:
        username = "free_user"
    
    while True:
        clear()
        key_bot()
        console.print("\n[bold cyan]OASIS AI MENU[/bold cyan]")
        console.print("[cyan]─" * 30 + "[/cyan]\n")
        
        if is_premium:
            console.print("[1] Register (Auto Reff)")
            console.print("[2] Login")
            console.print("[3] Create Providers")
            console.print("[4] Run Providers")
        else:
            console.print("[1] Login")
            console.print("[2] Create Providers")
            console.print("[3] Run Providers")
        
        console.print("[0] Keluar\n")
        console.print("[cyan]─" * 30 + "[/cyan]")
        
        choice = console.input("\n[bold white]Pilih menu (0-4): [/bold white]")
        
        if is_premium:
            if choice == "1":
                clear()
                key_bot()
                auto_reff(console, username)
            elif choice == "2":
                clear()
                key_bot()
                from api.login import login_from_file
                login_from_file('accounts.txt', console)
                console.input("\n[bold white]Tekan Enter untuk kembali ke menu[/bold white]")
            elif choice == "3":
                clear()
                key_bot()
                await create_providers(console, username, is_premium)
            elif choice == "4":
                clear()
                key_bot()
                await run_providers(console, username, is_premium)
        else:
            if choice == "1":
                clear()
                key_bot()
                from api.login import login_from_file
                login_from_file('accounts.txt', console)
                console.input("\n[bold white]Tekan Enter untuk kembali ke menu[/bold white]")
            elif choice == "2":
                clear()
                key_bot()
                await create_providers(console, username, is_premium)
            elif choice == "3":
                clear()
                key_bot()
                await run_providers(console, username, is_premium)
                
        if choice == "0":
            console.print("\n[cyan]Terima kasih telah menggunakan layanan kami[/cyan]")
            break
        elif choice not in ["0", "1", "2", "3", "4"]:
            console.print("\n[red]Pilihan tidak valid![/red]")
            time.sleep(1)

def auto_reff(console, username):
    """Fungsi untuk menangani fitur Auto Reff"""
    console.print("\n[bold cyan]OASIS AI REFERRAL[/bold cyan]")
    console.print("[cyan]─" * 30 + "[/cyan]\n")
    
    total_reff, max_reff = get_max_referral(username)
    if total_reff is None or max_reff is None:
        print_status("Gagal mendapatkan informasi referral", "error")
        return
        
    remaining_reff = max_reff - total_reff
    if remaining_reff <= 0:
        print_status(f"Batas maksimal referral ({max_reff}) telah tercapai", "error")
        return
        
    print_status(f"Sisa referral yang tersedia: {remaining_reff}", "info")
    
    num_referrals = int(console.input("[bold white]Jumlah referral : [/bold white]"))
    if num_referrals > remaining_reff:
        print_status(f"Jumlah referral melebihi batas tersisa ({remaining_reff})", "error")
        return
        
    max_threads = int(console.input("[bold white]Jumlah thread   : [/bold white]"))
    if max_threads < 1:
        max_threads = 1
    elif max_threads > 10:
        print_status("Maksimal 10 thread untuk menghindari rate limit", "warning")
        max_threads = 10
        
    referral_code = console.input("[bold white]Kode referral  : [/bold white]").strip()
    
    if not referral_code:
        referral_code = "itbaarts"
        print_status(f"\nMenggunakan kode referral: {referral_code}", "info")
    
    console.print()
    
    # Jalankan proses dengan threading
    process_referrals_threaded(num_referrals, referral_code, username, max_threads)
    
    console.print("\n")
    console.print("[cyan]─" * 30 + "[/cyan]")
    print_status("Proses selesai", "success")
    console.input("\n[bold white]Tekan Enter untuk kembali ke menu[/bold white]")

# Update entry point
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
