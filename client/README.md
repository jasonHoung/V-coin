# Client / API Layer

## 功能說明

客戶端層提供給終端使用者的介面，包括：
- Web Dashboard
- REST API
- SDK（Python / JavaScript / Go）
- CLI 工具

## API 服務

### 推論 API
```bash
POST /api/v1/inference
{
  "model_id": "llama-7b",
  "input": "你的問題",
  "parameters": {
    "max_length": 100,
    "temperature": 0.8
  }
}
```

### 訓練 API
```bash
POST /api/v1/training
{
  "model_id": "llama-7b",
  "dataset_url": "https://...",
  "lora_config": {
    "r": 8,
    "alpha": 16
  },
  "epochs": 3
}
```

### 查詢任務狀態
```bash
GET /api/v1/task/{task_id}/status
```

## SDK 使用

### Python SDK
```python
from vcoin import VCoinClient

client = VCoinClient(api_key="your-api-key")

# 推論
result = client.inference(
    model="llama-7b",
    prompt="介紹人工智慧"
)

# 訓練
job = client.train(
    model="llama-7b",
    dataset="path/to/dataset",
    lora_config={"r": 8, "alpha": 16}
)
```

### JavaScript SDK
```javascript
import { VCoinClient } from '@vcoin/sdk';

const client = new VCoinClient({ apiKey: 'your-api-key' });

// 推論
const result = await client.inference({
  model: 'llama-7b',
  prompt: '介紹人工智慧'
});
```

## Web Dashboard

提供視覺化介面：
- 任務管理
- 費用查詢
- 錢包管理
- 使用統計

## 開發計畫

- Phase 1: REST API + Python SDK
- Phase 2: Web Dashboard
- Phase 3: JavaScript SDK + CLI 工具
