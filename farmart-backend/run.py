#!/usr/bin/env python3

import os
from app import create_app

if __name__ == '__main__':
    # Load environment variables if .env file exists
    env_file = '.env'
    if os.path.exists(env_file):
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
