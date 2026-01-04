#!/usr/bin/env python3
"""
V-Coin 簡易平台測試伺服器（Python 版）
用於測試 GPU Agent 與平台的通訊
"""

from flask import Flask, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

# 簡單的記憶體儲存
tasks = {}
nodes = {}

@app.route('/health', methods=['GET'])
def health():
    """健康檢查"""
    return jsonify({"status": "ok"})

@app.route('/api/v1/inference', methods=['POST'])
def create_inference():
    """建立推論任務"""
    data = request.json
    
    task = {
        'id': str(uuid.uuid4()),
        'user_id': 'test-user',
        'type': 'inference',
        'model_id': data.get('model_id'),
        'input': data.get('input'),
        'parameters': data.get('parameters', {}),
        'status': 'pending',
        'result': None,
        'node_id': None,
        'created_at': datetime.now().isoformat()
    }
    
    tasks[task['id']] = task
    
    print(f"✅ 建立任務: {task['id']} (Model: {task['model_id']})")
    
    return jsonify(task)

@app.route('/api/v1/task/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """查詢任務狀態"""
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify(task)

@app.route('/api/v1/node/heartbeat', methods=['POST'])
def heartbeat():
    """處理節點心跳"""
    data = request.json
    node_id = data.get('node_id')
    
    if node_id not in nodes:
        # 新節點註冊
        nodes[node_id] = {
            'id': node_id,
            'gpu_model': data.get('gpu_model'),
            'gpu_memory': data.get('gpu_memory'),
            'status': data.get('status'),
            'reputation_score': 100.0,
            'last_heartbeat': datetime.now().isoformat()
        }
        print(f"🆕 新節點註冊: {node_id} ({data.get('gpu_model')})")
    else:
        nodes[node_id]['last_heartbeat'] = datetime.now().isoformat()
        nodes[node_id]['status'] = data.get('status')
    
    # 檢查是否有待處理任務
    has_task = any(task['status'] == 'pending' for task in tasks.values())
    
    return jsonify({
        'status': 'ok',
        'has_task': has_task
    })

@app.route('/api/v1/node/<node_id>/task', methods=['GET'])
def get_node_task(node_id):
    """節點獲取任務"""
    if node_id not in nodes:
        return jsonify({"error": "Node not found"}), 404
    
    # 找到第一個待處理任務
    for task in tasks.values():
        if task['status'] == 'pending':
            task['status'] = 'running'
            task['node_id'] = node_id
            print(f"📋 分配任務 {task['id']} 給節點 {node_id}")
            return jsonify(task)
    
    return jsonify({"error": "No tasks available"}), 404

@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    """獲取統計資訊"""
    return jsonify({
        'total_tasks': len(tasks),
        'pending_tasks': sum(1 for t in tasks.values() if t['status'] == 'pending'),
        'running_tasks': sum(1 for t in tasks.values() if t['status'] == 'running'),
        'total_nodes': len(nodes),
        'online_nodes': sum(1 for n in nodes.values() if n['status'] == 'online')
    })

if __name__ == '__main__':
    print("🚀 V-Coin Platform Server 啟動於 :8080")
    print("   健康檢查: http://localhost:8080/health")
    print("   統計資訊: http://localhost:8080/api/v1/stats")
    print()
    app.run(host='0.0.0.0', port=8080, debug=False)
