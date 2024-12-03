import asyncio
from api.logger import logger

async def read_token(file_path):
    try:
        with open(file_path, 'r') as f:
            tokens = [token.strip() for token in f.readlines() if token.strip()]
            
        if tokens:
            return tokens
        else:
            raise Exception('No tokens found')
            
    except Exception as e:
        raise Exception(f'Error reading tokens: {str(e)}')

async def read_accounts(file_path):
    try:
        with open(file_path, 'r') as f:
            accounts = []
            for line in f:
                line = line.strip()
                if '|' not in line:
                    continue
                    
                email, password = [part.strip() for part in line.split('|', 1)]
                if not email or not password:
                    continue
                    
                accounts.append({'email': email, 'password': password})
                
        if not accounts:
            logger('No valid accounts found in the file.', 'warning')
            
        return accounts
        
    except Exception as e:
        raise Exception(f'Error reading accounts: {str(e)}')

def save_token(file_path, token):
    try:
        with open(file_path, 'a') as f:
            f.write(f'{token}\n')
        logger('Token saved successfully.', 'success')
    except Exception as e:
        logger(f'Error saving token: {str(e)}', 'error')

async def delay(ms):
    await asyncio.sleep(ms/1000)