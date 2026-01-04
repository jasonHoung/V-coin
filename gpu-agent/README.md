# GPU Agent

## 功能說明

GPU Agent 運行在提供算力的節點上，負責：
- 定期向平台發送心跳
- 接收並執行推論/訓練任務
- 管理 Docker 容器
- 上傳執行結果

## 系統需求

- **作業系統**: Linux (Ubuntu 20.04+ 推薦)
- **GPU**: NVIDIA GPU（支援 CUDA）
- **CUDA**: 11.8+
- **Docker**: 20.10+
- **nvidia-docker**: 2.0+
- **Python**: 3.10+

## 安裝步驟

```bash
# 1. 安裝 NVIDIA Driver 與 CUDA
# 參考: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/

# 2. 安裝 Docker 與 nvidia-docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# 3. 安裝 Python 依賴
pip install -r requirements.txt

# 4. 配置 Agent
cp config.example.yaml config.yaml
# 編輯 config.yaml，填入節點資訊與平台 URL

# 5. 啟動 Agent
python main.py --config config.yaml
```

## 配置範例

```yaml
# config.yaml
node:
  id: "your-node-id"
  wallet_address: "0x..."
  
platform:
  api_url: "https://platform.vcoin.io/api/v1"
  websocket_url: "wss://platform.vcoin.io/ws"
  api_key: "your-api-key"

gpu:
  device_id: 0  # CUDA device ID
  max_memory: 24576  # MB

agent:
  heartbeat_interval: 30  # 秒
  log_level: "INFO"
```

## 運行狀態監控

```bash
# 查看 GPU 狀態
nvidia-smi

# 查看 Agent 日誌
tail -f logs/agent.log

# 查看容器狀態
docker ps
```

## 安全注意事項

- Agent 僅與平台通訊，不對外開放端口
- 所有任務在 Docker 容器中隔離執行
- 定期更新 Agent 版本以獲得安全修復
- 妥善保管錢包私鑰

## 開發指南

詳見 [開發實作指南](../docs/05-開發實作指南.md#12-gpu-agent-開發)
