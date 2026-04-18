import requests
import time
import asyncio
from datetime import datetime

class BotMonitor:
    def __init__(self, check_url="http://localhost:8080/status", interval=300):
        self.check_url = check_url
        self.interval = interval  # 5 minutos
        self.last_check = None
        self.failures = 0
        
    async def health_check(self):
        """Verifica se o bot está respondendo"""
        try:
            response = requests.get(self.check_url, timeout=10)
            if response.status_code == 200:
                self.failures = 0
                self.last_check = datetime.now()
                print(f"✓ Health check OK - {self.last_check.strftime('%H:%M:%S')}")
                return True
            else:
                self.failures += 1
                print(f"⚠️ Health check failed - Status: {response.status_code}")
                return False
        except Exception as e:
            self.failures += 1
            print(f"❌ Health check error: {str(e)}")
            return False
    
    async def start_monitoring(self):
        """Inicia o monitoramento contínuo"""
        print("🔍 Iniciando monitoramento do bot...")
        while True:
            await self.health_check()
            
            if self.failures >= 3:
                print("🚨 Bot com falhas críticas detectadas!")
            
            await asyncio.sleep(self.interval)

if __name__ == "__main__":
    monitor = BotMonitor()
    asyncio.run(monitor.start_monitoring())