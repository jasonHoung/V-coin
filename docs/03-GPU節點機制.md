# GPU 節點機制設計

## 一、GPU Agent 架構

### 1.1 整體架構

```
┌─────────────────────────────────────┐
│        Platform Server              │
│  - 任務分配                          │
│  - 驗證管理                          │
│  - 獎勵結算                          │
└────────────┬────────────────────────┘
             │ HTTPS/WebSocket
┌────────────▼────────────────────────┐
│       GPU Agent Daemon              │
│  ┌──────────────────────────────┐   │
│  │  Heartbeat Monitor           │   │
│  │  - 心跳上報（每30秒）          │   │
│  │  - GPU 狀態監控               │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │  Task Receiver               │   │
│  │  - 接收推論/訓練任務           │   │
│  │  - 任務佇列管理                │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │  Docker Manager              │   │
│  │  - 容器生命週期管理            │   │
│  │  - GPU 資源分配               │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │  Result Uploader             │   │
│  │  - 結果加密上傳                │   │
│  │  - 斷點續傳                    │   │
│  └──────────────────────────────┘   │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│     Docker Container (GPU)          │
│  ┌──────────────────────────────┐   │
│  │  Model Executor              │   │
│  │  - PyTorch/TensorFlow        │   │
│  │  - Hugging Face Transformers │   │
│  │  - CUDA Runtime              │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

### 1.2 Agent Daemon 核心模組

#### Heartbeat Monitor
```python
class HeartbeatMonitor:
    def __init__(self):
        self.interval = 30  # 秒
        
    def collect_status(self):
        return {
            'gpu_model': get_gpu_model(),
            'gpu_memory': get_gpu_memory(),
            'gpu_utilization': get_gpu_utilization(),
            'temperature': get_gpu_temperature(),
            'cuda_version': get_cuda_version(),
            'reputation_score': get_local_reputation(),
            'staked_amount': get_staked_vcoin()
        }
    
    def send_heartbeat(self):
        status = self.collect_status()
        response = platform_api.heartbeat(status)
        if response.has_task:
            task_receiver.fetch_task()
```

#### Task Receiver
```python
class TaskReceiver:
    def fetch_task(self):
        task = platform_api.get_task(self.agent_id)
        if task.type == 'inference':
            self.handle_inference(task)
        elif task.type == 'training':
            self.handle_training(task)
    
    def handle_inference(self, task):
        # 下載模型（如未快取）
        model_path = download_model(task.model_id)
        
        # 啟動 Docker 容器
        container = docker_manager.run_inference(
            model_path=model_path,
            input_data=task.input,
            gpu_id=task.gpu_id
        )
        
        # 等待結果
        result = container.wait_for_result(timeout=task.timeout)
        
        # 上傳結果
        result_uploader.upload(task.id, result)
```

## 二、任務接收與執行

### 2.1 推論任務流程

```
1. Agent 心跳 → Platform 返回有新任務
2. Agent 拉取任務詳情（模型、輸入、參數）
3. 檢查本地模型快取
   - 有 → 直接載入
   - 無 → 從 CDN 下載並驗證 checksum
4. 啟動 Docker 容器
   - 掛載模型（唯讀）
   - 注入輸入資料
   - 限制 GPU 記憶體
5. 執行推論
   - 超時監控（預設120秒）
   - GPU 溫度監控
6. 收集輸出
7. 上傳結果至 Platform
8. 等待驗證確認
9. 獲得 VCoin 獎勵
```

### 2.2 訓練任務流程

```
1. 接收訓練任務（資料集分片）
2. 下載基礎模型 + LoRA 配置
3. 啟動訓練容器
4. 執行 LoRA 訓練
   - 每 N steps 上傳梯度
   - 接收聚合後的權重
5. 完成訓練
6. 上傳最終 LoRA 權重
7. Platform 驗證權重有效性
8. 獲得訓練獎勵
```

## 三、Docker 容器管理

### 3.1 推論容器配置

```yaml
# docker-compose.yml
version: '3.8'
services:
  inference:
    image: vcoin/inference:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=${GPU_ID}
      - MODEL_PATH=/models/${MODEL_NAME}
      - MAX_MEMORY=24GB
      - TIMEOUT=120
    volumes:
      - ./models:/models:ro
      - ./input:/input:ro
      - ./output:/output:rw
    networks:
      - vcoin-net
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 3.2 訓練容器配置

```yaml
services:
  training:
    image: vcoin/training:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=${GPU_ID}
      - TRAINING_TYPE=lora
      - GRADIENT_SYNC_INTERVAL=100
    volumes:
      - ./datasets:/data:ro
      - ./checkpoints:/checkpoints:rw
    shm_size: '8gb'  # 共享記憶體用於 DataLoader
```

### 3.3 安全隔離措施

```dockerfile
# Dockerfile 範例
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# 建立非 root 使用者
RUN useradd -m -u 1000 vcoin-worker

# 安裝必要套件
RUN apt-get update && apt-get install -y \
    python3.10 \
    && rm -rf /var/lib/apt/lists/*

# 複製執行環境
COPY --chown=vcoin-worker:vcoin-worker . /app
WORKDIR /app

# 切換至非特權使用者
USER vcoin-worker

# 限制網路存取（僅允許回傳結果）
# 在 docker-compose 層級配置

CMD ["python3", "executor.py"]
```

## 四、驗證流程

### 4.1 推論結果驗證

**本地驗證**
```python
def local_validate(result):
    # 1. 檢查輸出格式
    if not is_valid_format(result):
        return False
    
    # 2. 檢查輸出範圍
    if result.out_of_bounds():
        return False
    
    # 3. 計算輸出 hash
    result_hash = sha256(result.output)
    
    return True
```

**平台驗證**（抽樣 10%）
```python
def platform_validate(task_id, result):
    # 1. 重新分配給另一個高信譽節點
    verify_task = create_verification_task(task_id)
    verify_result = assign_to_validator(verify_task)
    
    # 2. 比對結果
    similarity = compute_similarity(result, verify_result)
    
    # 3. 判定
    if similarity > 0.95:
        return PASS
    elif similarity > 0.85:
        return NEED_HUMAN_REVIEW
    else:
        return FAIL
```

### 4.2 訓練權重驗證

```python
def validate_training_weights(lora_weights):
    # 1. 檢查權重維度
    if not check_dimensions(lora_weights):
        return False
    
    # 2. 檢查數值範圍（防止 NaN/Inf）
    if has_invalid_values(lora_weights):
        return False
    
    # 3. 在驗證資料集上測試
    loss = evaluate_on_validation_set(lora_weights)
    if loss > THRESHOLD:
        return False
    
    return True
```

## 五、信譽系統整合

### 5.1 信譽分數計算

```python
class ReputationManager:
    def calculate_score(self, node_id):
        stats = get_node_statistics(node_id)
        
        # 成功率（權重 50%）
        success_rate = stats.success_tasks / stats.total_tasks
        
        # 回應速度（權重 20%）
        avg_response_time = stats.total_response_time / stats.total_tasks
        response_score = 1.0 / (1 + avg_response_time / 60)  # 正規化
        
        # 正常運行時間（權重 20%）
        uptime_score = stats.uptime_hours / (stats.days_active * 24)
        
        # 質押權重（權重 10%）
        stake_score = min(stats.staked_amount / RECOMMENDED_STAKE, 1.0)
        
        final_score = (
            success_rate * 0.5 +
            response_score * 0.2 +
            uptime_score * 0.2 +
            stake_score * 0.1
        ) * 100
        
        return final_score
    
    def update_on_success(self, node_id):
        # 成功完成任務，小幅提升
        current_score = self.get_score(node_id)
        new_score = min(current_score + 0.1, 100)
        self.set_score(node_id, new_score)
    
    def update_on_failure(self, node_id, severity):
        # 失敗，根據嚴重性降低
        penalty = {
            'light': 5,
            'medium': 15,
            'severe': 30
        }
        current_score = self.get_score(node_id)
        new_score = max(current_score - penalty[severity], 0)
        self.set_score(node_id, new_score)
        
        # 觸發 Slashing
        if severity == 'severe':
            self.slash_stake(node_id, ratio=0.5)
```

### 5.2 任務分配優先級

```python
def select_node_for_task(task):
    available_nodes = get_available_nodes(task.gpu_requirement)
    
    # 根據信譽排序
    sorted_nodes = sorted(
        available_nodes,
        key=lambda n: (n.reputation_score, n.staked_amount),
        reverse=True
    )
    
    # 高信譽節點優先獲得任務
    return sorted_nodes[0]
```

## 六、獎勵結算

### 6.1 推論獎勵

```python
def calculate_inference_reward(task):
    base_reward = task.user_payment * 0.9  # 10% 燃燒
    
    # 信譽加成
    reputation_multiplier = get_reputation_multiplier(task.node_id)
    
    # 速度加成（早於預期完成）
    speed_bonus = 0
    if task.actual_time < task.expected_time * 0.8:
        speed_bonus = base_reward * 0.1
    
    total_reward = base_reward * reputation_multiplier + speed_bonus
    
    return total_reward
```

### 6.2 訓練獎勵

```python
def calculate_training_reward(task):
    # 基礎獎勵：時薪制
    base_reward = task.gpu_hours * GPU_HOURLY_RATE
    
    # 品質加成（根據驗證結果）
    quality_score = validate_training_quality(task.weights)
    quality_multiplier = quality_score / 100
    
    # 貢獻加成（訓練資料量）
    data_contribution = task.processed_samples / task.total_samples
    
    total_reward = (
        base_reward * 
        quality_multiplier * 
        (1 + data_contribution * 0.2)
    )
    
    return total_reward
```

## 七、故障處理

### 7.1 節點離線處理

```
1. 超過 5 分鐘未回應心跳 → 標記為離線
2. 重新分配該節點的進行中任務
3. 暫停新任務分配
4. 每日扣除質押金 1%（超過7天）
5. 恢復上線後需重新驗證
```

### 7.2 任務失敗重試

```python
def handle_task_failure(task):
    task.retry_count += 1
    
    if task.retry_count < MAX_RETRIES:
        # 重新分配給不同節點
        new_node = select_different_node(task.failed_nodes)
        reassign_task(task, new_node)
    else:
        # 達到最大重試次數
        refund_user(task.user_id, task.payment)
        mark_all_failed_nodes(task)
```

## 八、監控與告警

### 8.1 關鍵指標

```
- 平均任務完成時間
- 任務失敗率
- GPU 溫度
- 記憶體使用率
- 網路延遲
- 驗證通過率
```

### 8.2 告警機制

```python
def check_node_health(node_id):
    metrics = get_node_metrics(node_id)
    
    if metrics.gpu_temp > 85:
        alert('GPU 過熱', node_id)
        pause_node(node_id)
    
    if metrics.failure_rate > 0.2:
        alert('失敗率過高', node_id)
        increase_validation_rate(node_id)
    
    if metrics.avg_delay > 10:
        alert('網路延遲過高', node_id)
        lower_priority(node_id)
```
