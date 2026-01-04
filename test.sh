#!/bin/bash

# V-Coin 測試腳本

echo "🧪 V-Coin 系統測試"
echo "===================="
echo ""

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 測試 1: 健康檢查
echo -e "${YELLOW}測試 1: 平台健康檢查${NC}"
HEALTH=$(curl -s http://localhost:8080/health)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 平台運行中${NC}"
    echo "   回應: $HEALTH"
else
    echo -e "${RED}✗ 平台未運行${NC}"
    echo "   請先啟動平台: cd platform && go run main.go"
    exit 1
fi
echo ""

# 測試 2: 建立推論任務
echo -e "${YELLOW}測試 2: 建立推論任務${NC}"
TASK_RESPONSE=$(curl -s -X POST http://localhost:8080/api/v1/inference \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "llama-7b",
    "input": "什麼是人工智慧？",
    "parameters": {
      "max_length": 100,
      "temperature": 0.8
    }
  }')

TASK_ID=$(echo $TASK_RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ ! -z "$TASK_ID" ]; then
    echo -e "${GREEN}✓ 任務建立成功${NC}"
    echo "   Task ID: $TASK_ID"
else
    echo -e "${RED}✗ 任務建立失敗${NC}"
    exit 1
fi
echo ""

# 測試 3: 查詢任務狀態
echo -e "${YELLOW}測試 3: 查詢任務狀態${NC}"
sleep 1
TASK_STATUS=$(curl -s http://localhost:8080/api/v1/task/$TASK_ID/status)
STATUS=$(echo $TASK_STATUS | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ ! -z "$STATUS" ]; then
    echo -e "${GREEN}✓ 查詢成功${NC}"
    echo "   狀態: $STATUS"
else
    echo -e "${RED}✗ 查詢失敗${NC}"
fi
echo ""

# 測試 4: 模擬節點心跳
echo -e "${YELLOW}測試 4: 模擬節點心跳${NC}"
NODE_ID="test-node-$(date +%s)"
HEARTBEAT_RESPONSE=$(curl -s -X POST http://localhost:8080/api/v1/node/heartbeat \
  -H "Content-Type: application/json" \
  -d "{
    \"node_id\": \"$NODE_ID\",
    \"gpu_model\": \"RTX 3090\",
    \"gpu_memory\": 24576,
    \"gpu_utilization\": 0.0,
    \"temperature\": 65.0,
    \"status\": \"online\"
  }")

HAS_TASK=$(echo $HEARTBEAT_RESPONSE | grep -o '"has_task":[^,}]*' | cut -d':' -f2)

if [ ! -z "$HAS_TASK" ]; then
    echo -e "${GREEN}✓ 心跳成功${NC}"
    echo "   有任務: $HAS_TASK"
else
    echo -e "${RED}✗ 心跳失敗${NC}"
fi
echo ""

# 測試 5: 節點獲取任務
echo -e "${YELLOW}測試 5: 節點獲取任務${NC}"
ASSIGNED_TASK=$(curl -s http://localhost:8080/api/v1/node/$NODE_ID/task)
ASSIGNED_TASK_ID=$(echo $ASSIGNED_TASK | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ ! -z "$ASSIGNED_TASK_ID" ]; then
    echo -e "${GREEN}✓ 任務分配成功${NC}"
    echo "   分配的任務: $ASSIGNED_TASK_ID"
else
    echo -e "${YELLOW}⚠ 無可用任務${NC}"
fi
echo ""

# 測試總結
echo "===================="
echo -e "${GREEN}✓ 測試完成${NC}"
echo ""
echo "建議下一步:"
echo "1. 在另一個終端啟動 GPU Agent: cd gpu-agent && python main.py"
echo "2. 觀察 Agent 自動接收並處理任務"
echo "3. 建立更多任務測試分配機制"
