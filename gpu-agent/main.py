#!/usr/bin/env python3
"""
V-Coin GPU Agent
負責接收任務、執行推論、上傳結果
"""

import json
import time
import uuid
import requests
from datetime import datetime


class GPUAgent:
    def __init__(self, config):
        self.node_id = config.get('node_id', str(uuid.uuid4()))
        self.platform_url = config.get('platform_url', 'http://localhost:8080')
        self.gpu_model = config.get('gpu_model', 'Test-GPU')
        self.gpu_memory = config.get('gpu_memory', 8192)
        self.heartbeat_interval = config.get('heartbeat_interval', 30)
        self.running = True
        
    def start(self):
        print(f"🚀 GPU Agent 啟動")
        print(f"   Node ID: {self.node_id}")
        print(f"   GPU: {self.gpu_model} ({self.gpu_memory}MB)")
        print(f"   Platform: {self.platform_url}")
        print()
        
        try:
            while self.running:
                self.heartbeat_loop()
                time.sleep(self.heartbeat_interval)
        except KeyboardInterrupt:
            print("\n⏹️  Agent 停止")
    
    def heartbeat_loop(self):
        """心跳循環"""
        try:
            # 發送心跳
            response = self.send_heartbeat()
            
            if response and response.get('has_task'):
                print("📨 發現新任務")
                self.fetch_and_execute_task()
                
        except Exception as e:
            print(f"❌ 心跳錯誤: {e}")
    
    def send_heartbeat(self):
        """發送心跳"""
        data = {
            'node_id': self.node_id,
            'gpu_model': self.gpu_model,
            'gpu_memory': self.gpu_memory,
            'gpu_utilization': 0.0,  # 模擬數據
            'temperature': 65.0,      # 模擬數據
            'status': 'online'
        }
        
        try:
            resp = requests.post(
                f"{self.platform_url}/api/v1/node/heartbeat",
                json=data,
                timeout=5
            )
            
            if resp.status_code == 200:
                result = resp.json()
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"💓 [{timestamp}] 心跳正常 - 有任務: {result.get('has_task', False)}")
                return result
            else:
                print(f"⚠️  心跳回應異常: {resp.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  無法連接平台: {e}")
            
        return None
    
    def fetch_and_execute_task(self):
        """獲取並執行任務"""
        try:
            # 獲取任務
            resp = requests.get(
                f"{self.platform_url}/api/v1/node/{self.node_id}/task",
                timeout=5
            )
            
            if resp.status_code == 200:
                task = resp.json()
                print(f"\n📋 收到任務:")
                print(f"   Task ID: {task['id']}")
                print(f"   Type: {task['type']}")
                print(f"   Model: {task['model_id']}")
                print(f"   Input: {task['input'][:50]}...")
                
                # 執行任務（模擬）
                result = self.execute_task(task)
                print(f"✅ 任務完成: {result[:50]}...")
                print()
                
            elif resp.status_code == 404:
                print("ℹ️  暫無可用任務")
            else:
                print(f"⚠️  獲取任務失敗: {resp.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 獲取任務錯誤: {e}")
    
    def execute_task(self, task):
        """執行任務（模擬）"""
        print("⚙️  執行推論中...")
        time.sleep(2)  # 模擬執行時間
        
        # 模擬推論結果
        if task['type'] == 'inference':
            result = f"這是對 '{task['input']}' 的模擬回應。"
            return result
        
        return "任務完成"


def load_config():
    """載入配置"""
    return {
        'node_id': f"node-{uuid.uuid4().hex[:8]}",
        'platform_url': 'http://localhost:8080',
        'gpu_model': 'RTX 3090 (模擬)',
        'gpu_memory': 24576,
        'heartbeat_interval': 10
    }


if __name__ == '__main__':
    config = load_config()
    agent = GPUAgent(config)
    agent.start()
