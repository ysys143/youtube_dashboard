import subprocess
import os

def run_npm():
    # 현재 디렉토리에서 carousel_component/frontend로 이동
    npm_dir = os.path.join(os.path.dirname(__file__), '..', 'carousel_component', 'frontend')
    
    # npm start 명령 실행
    subprocess.Popen(['npm', 'start'], cwd=npm_dir)