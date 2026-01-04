# 🚀 V-Coin 快速啟動指南

## 一鍵啟動測試

### 方式 1: 分步驟啟動（推薦用於學習）
要開不同的終端機！！！
#### 步驟 1: 啟動平台
```bash
# 終端 1
cd V-coin
python3 platform/server.py
```

等待看到：
```
🚀 V-Coin Platform Server 啟動於 :8080
```

#### 步驟 2: 啟動 GPU Agent
```bash
# 終端 2  
cd V-coin/gpu-agent
python3 main.py
```

等待看到：
```
🚀 GPU Agent 啟動
   Node ID: node-xxxxxxxx
💓 心跳正常
```

#### 步驟 3: 建立任務
```bash
# 終端 3
curl -X POST http://localhost:8080/api/v1/inference \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "llama-7b",
    "input": "什麼是人工智慧？"
  }'
```

觀察終端 2 的 Agent 自動處理任務！

### 方式 2: 背景執行

```bash
cd V-coin

# 啟動平台（背景）
python3 platform/server.py > platform.log 2>&1 &

# 等待2秒
sleep 2

# 啟動 Agent（背景）
cd gpu-agent && python3 main.py > agent.log 2>&1 &

# 建立測試任務
curl -X POST http://localhost:8080/api/v1/inference \
  -H "Content-Type: application/json" \
  -d '{"model_id":"llama-7b","input":"測試"}'

# 查看統計
curl http://localhost:8080/api/v1/stats

# 查看日誌
tail -f platform.log
tail -f gpu-agent/agent.log
```

### 方式 3: 自動化測試腳本

```bash
chmod +x test.sh
./test.sh
```

---

## 快速測試命令

### 健康檢查
```bash
curl http://localhost:8080/health
```

### 建立任務
```bash
curl -X POST http://localhost:8080/api/v1/inference \
  -H "Content-Type: application/json" \
  -d '{"model_id":"llama-7b","input":"你的問題"}'
```

### 查看統計
```bash
curl http://localhost:8080/api/v1/stats | python3 -m json.tool
```

### 查詢任務狀態
```bash
# 替換 TASK_ID
curl http://localhost:8080/api/v1/task/TASK_ID/status
```

---

## 停止服務

### 停止背景進程
```bash
# 查找進程
ps aux | grep "server.py\|main.py"

# 或使用 pkill
pkill -f "server.py"
pkill -f "gpu-agent/main.py"
```

### 停止前台進程
按 `Ctrl+C`

---

## 常見問題

### Q: 端口被占用
```bash
# 檢查占用
lsof -i :8080

# 殺掉占用進程
kill -9 PID
```

### Q: 依賴未安裝
```bash
# 安裝 platform 依賴
cd platform
pip3 install -r requirements.txt

# 安裝 agent 依賴
cd ../gpu-agent
pip3 install -r requirements.txt
```

### Q: curl 不可用
macOS 和 Linux 預裝 curl，如果沒有：
```bash
brew install curl  # macOS
```

或使用瀏覽器訪問：
- 健康檢查: http://localhost:8080/health
- 統計資訊: http://localhost:8080/api/v1/stats

---

## 測試場景

### 場景 1: 單任務處理
1. 啟動平台和 Agent
2. 建立一個任務
3. 觀察 Agent 自動處理

### 場景 2: 批量任務
```bash
for i in {1..10}; do
  curl -X POST http://localhost:8080/api/v1/inference \
    -H "Content-Type: application/json" \
    -d "{\"model_id\":\"llama-7b\",\"input\":\"問題 $i\"}"
done
```

### 場景 3: 多 Agent
在不同終端啟動多個 Agent，觀察任務分配：
```bash
# 終端 2
python3 main.py

# 終端 3
python3 main.py

# 終端 4
python3 main.py
```

---

## 監控命令

### 即時監控統計
```bash
watch -n 2 'curl -s http://localhost:8080/api/v1/stats | python3 -m json.tool'
```

### 查看所有日誌
```bash
tail -f platform.log agent.log
```

---

## 預期輸出

### 正常運行時
**Platform**:
```
🚀 V-Coin Platform Server 啟動於 :8080
✅ 建立任務: xxx-xxx (Model: llama-7b)
🆕 新節點註冊: node-abc (RTX 3090)
📋 分配任務 xxx-xxx 給節點 node-abc
```

**Agent**:
```
🚀 GPU Agent 啟動
💓 [時間] 心跳正常 - 有任務: True
📨 發現新任務
📋 收到任務: xxx-xxx
⚙️  執行推論中...
✅ 任務完成
```

---

## 下一步

測試完成後，可以：
1. 查看 [TEST-REPORT.md](./TEST-REPORT.md) 了解詳細測試結果
2. 閱讀 [docs/](./docs/) 目錄中的技術文檔
3. 參考 [開發實作指南](./docs/05-開發實作指南.md) 繼續開發

---

**提示**: 這是模擬測試環境，實際 GPU 執行需要完成 Phase 1 完整開發
