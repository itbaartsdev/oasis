import requests
import json
from api.logger import print_status
import time

def register_user(email, password):
    """Fungsi untuk mendaftarkan user"""
    url = 'https://api.oasis.ai/internal/authSignup?batch=1'
    payload = {
        "0": {
            "json": {
                "email": email,
                "password": password,
                "referralCode": "itbaarts"
            }
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.ok and response.json()[0].get('result'):
            print_status(f'Registrasi berhasil: {email}', 'success')
            print_status('Silakan cek email untuk verifikasi', 'info')
            return True
    except Exception as e:
        print_status(f'Error registrasi untuk {email}: {str(e)}', 'error')
    return False

def login_user(email, password, proxy=None):
    """Fungsi untuk login user dengan dukungan proxy"""
    url = 'https://api.oasis.ai/internal/authLogin?batch=1'
    payload = {
        "0": {
            "json": {
                "email": email,
                "password": password,
                "rememberSession": True
            }
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }

    session = requests.Session()
    
    if proxy:
        session.proxies = {
            'http': proxy,
            'https': proxy
        }
        session.verify = False
    
    try:
        response = session.post(
            url, 
            json=payload,
            headers=headers,
            timeout=30
        )
        if response.ok:
            data = response.json()
            token = data[0]['result']['data']['json']['token']
            print_status(f'Login berhasil: {email}', 'success')
            return token
    except Exception as e:
        print_status(f'Error login untuk {email}: {str(e)}', 'error')
        print_status('Silakan cek email untuk verifikasi akun', 'warning')
    return None

def read_accounts(file_path):
    """Membaca daftar akun dari file"""
    accounts = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if '|' in line:
                    email, password = line.strip().split('|')
                    accounts.append({'email': email, 'password': password})
        return accounts
    except Exception as e:
        print_status(f'Error membaca file: {str(e)}', 'error')
        return []

def save_token(file_path, token):
    """Menyimpan token ke file"""
    try:
        with open(file_path, 'a') as f:
            f.write(f'{token}\n')
        return True
    except Exception as e:
        print_status(f'Error menyimpan token: {str(e)}', 'error')
        return False

def login_from_file(file_path, console):
    """Fungsi utama untuk login dari file"""
    try:
        accounts = read_accounts(file_path)
        if not accounts:
            print_status('Tidak ada akun yang ditemukan', 'error')
            return False

        success_count = 0
        total = len(accounts)

        console.print("\n[bold cyan]PROSES LOGIN AKUN[/bold cyan]")
        console.print("[cyan]─" * 30 + "[/cyan]\n")

        for i, account in enumerate(accounts, 1):
            console.print(f"\n[{i}/{total}] Mencoba login: {account['email']}")
            
            token = login_user(account['email'], account['password'])
            if token:
                save_token('tokens.txt', token)
                success_count += 1
            else:
                console.print(f"[yellow]Mencoba registrasi untuk: {account['email']}[/yellow]")
                register_user(account['email'], account['password'])
            
            # Delay untuk menghindari rate limit
            time.sleep(1)

        if success_count > 0:
            print_status(f'{success_count}/{total} akun berhasil login', 'success')
            return True
        else:
            print_status('Semua akun gagal login', 'error')
            return False

    except Exception as e:
        print_status(f'Error: {str(e)}', 'error')
        return False
