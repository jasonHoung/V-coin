# V-Coin 測試指南

## 快速開始測試

### 前置需求

#### Platform (Go)
```bash
# 安裝 Go (如果尚未安裝)
brew install go  # macOS
# 或從 https://go.dev/dl/ 下載

# 檢查版本
go version  # 需要 1.21+
```

#### GPU Agent (Python)
```bash
# 檢查 Python 版本
python3 --version  # 需要 3.10+

# 安裝依賴
cd gpu-agent
pip3 install -r requirements.txt
```

## 測試步驟

### 方法 1: 自動化測試腳本

1. **啟動平台**
```bash
# 終端 1
cd platform
go mod download
go run main.go
```

等待看到：
```
🚀 V-Coin Platform Server 啟動於 :8080
```

2. **執行測試**
```bash
# 終端 2
chmod +x test.sh
./test.sh
```

3. **啟動 GPU Agent**
```bash
# 終端 3
cd gpu-agent
python3 main.py
```

### 方法 2: 手動測試

#### 1. 測試平台健康檢查
```bash
curl http://localhost:8080/health
```

預期輸出：
```json
{"status":"ok"}
```

#### 2. 建立推論任務
```bash
curl -X POST http://localhost:8080/api/v1/inference \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "llama-7b",
    "input": "什麼是人工智慧？",
    "parameters": {
      "max_length": 100,
      "temperature": 0.8
    }
  }'
```

預期輸出：
```json
{
  "id": "uuid-here",
  "type": "inference",
  "model_id": "llama-7b",
  "status": "pending",
  ...
}
```

#### 3. 查詢任務狀態
```bash
# 替換 {task_id} 為上一步得到的 ID
curl http://localhost:8080/api/v1/task/{task_id}/status
```

#### 4. 啟動 GPU Agent（自動處理任務）
```bash
cd gpu-agent
python3 main.py
```

觀察 Agent 自動：
- 發送心跳
- 發現任務
- 執行任務
- 回報結果

## 測試場景

### 場景 1: 基礎推論流程
1. 啟動平台
2. 建立推論任務
3. 啟動 Agent
4. 觀察任務被自動處理

### 場景 2: 多節點測試
1. 啟動平台
2. 建立多個任務
3. 啟動多個 Agent（不同終端）
4. 觀察任務分配

### 場景 3: 心跳監控
1. 啟動平台和 Agent
2. 觀察定期心跳
3. 停止 Agent
4. 確認平台檢測到節點離線

## 預期輸出範例

### Platform 輸出
```
🚀 V-Coin Platform Server 啟動於 :8080
✅ 建立任務: abc-123 (Model: llama-7b)
🆕 新節點註冊: node-xyz (RTX 3090)
📋 分配任務 abc-123 給節點 node-xyz
```

### GPU Agent 輸出
```
🚀 GPU Agent 啟動
   Node ID: node-xyz
   GPU: RTX 3090 (模擬) (24576MB)
   Platform: http://localhost:8080

💓 [14:30:00] 心跳正常 - 有任務: True
📨 發現新任務

📋 收到任務:
   Task ID: abc-123
   Type: inference
   Model: llama-7b
   Input: 什麼是人工智慧？...

⚙️  執行推論中...
✅ 任務完成: 這是對 '什麼是人工智慧？' 的模擬回應。
```

## 測試驗證清單

- [ ] 平台成功啟動
- [ ] 健康檢查正常
- [ ] 可建立推論任務
- [ ] 可查詢任務狀態
- [ ] Agent 成功連接平台
- [ ] Agent 可接收任務
- [ ] Agent 可執行任務
- [ ] 心跳機制正常運作
- [ ] 多個 Agent 可同時運行
- [ ] 任務可正確分配

## 下一步

完成基礎測試後，可以：

1. **加入資料庫**: 將記憶體儲存改為 PostgreSQL
2. **實現驗證**: 加入任務驗證機制
3. **整合 Docker**: 實際使用 Docker 容器執行推論
4. **加入 Blockchain**: 整合智能合約進行獎勵結算
5. **壓力測試**: 測試大量任務與節點

## 故障排除

### 問題: 平台無法啟動
```bash
# 檢查端口是否被占用
lsof -i :8080

# 或更換端口
# 編輯 main.go，將 :8080 改為其他端口
```

### 問題: Agent 無法連接
```bash
# 確認平台運行中
curl http://localhost:8080/health

# 檢查防火牆設置
# 確認 config 中的 URL 正確
```

### 問題: Go 依賴下載失敗
```bash
# 使用國內代理
go env -w GOPROXY=https://goproxy.cn,direct
go mod download
```

## 測試數據

目前實現為**模擬測試**：
- ✅ API 路由與請求處理
- ✅ 任務建立與查詢
- ✅ 節點註冊與心跳
- ✅ 任務分配邏輯
- ⚠️ 實際 GPU 執行（需 Phase 1 完整開發）
- ⚠️ 資料庫持久化（目前使用記憶體）
- ⚠️ 結果驗證機制（待實現）

這個測試環境驗證了：
1. 系統架構可行性
2. API 設計合理性
3. Agent-Platform 通訊流程
4. 任務調度邏輯

## 貢獻測試

歡迎提交測試案例：
- 邊界條件測試
- 錯誤處理測試
- 性能測試腳本
- 安全測試場景
