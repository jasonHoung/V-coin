# V-coin

一、整體系統分層架構
架構分層總覽
【Client / Customer Layer】
│
├─ Web Console（客戶後台）
├─ REST / gRPC API（商用客戶）
│
▼
【Platform Control Layer（你控制的核心）】
│
├─ Auth / Billing / Rate Limit
├─ Job Manager（訓練 / 推論）
├─ Scheduler（GPU 調度）
├─ Verifier（結果驗證）
├─ Reputation System（節點信譽）
│
▼
【Compute Layer（用戶 GPU）】
│
├─ GPU Node Agent
│   ├─ Task Runner
│   ├─ Proof Generator
│   └─ Heartbeat Monitor
│
▼
【Settlement Layer（鏈上）】
│
├─ ERC-20 Token
├─ Reward Distributor
└─ Staking Contract

二、各層詳細說明（實作導向）
1️⃣ Client / Customer Layer（收入入口）
功能
提交 AI 任務
查詢任務狀態
下載結果
消耗代幣
技術建議
Web：Next.js / Vue
API：REST（推論）＋ gRPC（批次）
Auth：API Key + JWT
商用重點
不讓客戶知道 GPU 來自哪
客戶只看到 SLA、速度、價格

2️⃣ Platform Control Layer
這一層100% 中心化，是你風險控制與商業護城河。
2.1 Job Manager（任務管理）
職責
接收訓練 / 推論請求
任務切分
任務狀態管理
任務類型
INFERENCE_JOB
TRAIN_LORA_JOB
TRAIN_BATCH_JOB
任務資料結構（示意）
Job {
  job_id
  job_type
  model_id
  dataset_ref
  required_gpu_vram
  reward_rate
  verification_level
}

2.2 Scheduler
決策依據
GPU 型號
VRAM
節點信譽
在線時間
當前負載
排程策略（初期）
高信譽節點優先
新節點只給低風險任務
訓練與推論分池
2.3 Verifier（防作弊關鍵）
Verifier 不在鏈上，效能與安全都比較好。
驗證方式
任務重複抽樣（2–3 節點）
輸出 Hash 比對
訓練 Loss / Checkpoint 驗證
隱藏測試樣本
2.4 Reputation System（節點信譽）
影響
接單優先權
單位時間收益
可接任務類型
指標
成功率
結果一致率
在線穩定度
歷史作弊紀錄

3️⃣ Compute Layer
GPU Node Agent（你要發給使用者的）
Agent 組成
GPU Agent
├─ Node Auth（節點註冊）
├─ Task Receiver
├─ Docker Executor
├─ Proof Generator
└─ Result Uploader
安全設計（非常重要）
任務 Docker 沙箱化
不可存取宿主系統
限制網路出口
任務結束即銷毀容器
Proof of Computation（簡化實用版）
節點回傳：
Output
GPU 使用紀錄
任務執行時間
中間結果 Hash

4️⃣ Settlement Layer（鏈上只做「記帳」）
為什麼鏈上要最小化？
Gas 成本
法規風險
效能瓶頸
智慧合約角色
ERC-20 Token
平台結算單位
不具投資承諾
Reward Distributor
每日 / 每小時批次發放
由平台簽名授權
Staking Contract
GPU 節點需質押
作為作弊懲罰機制

5️⃣ 資料與模型管理
模型
中央儲存（S3 / GCS）
節點只下載必要部分
加密存放
資料集
不直接下發完整原始資料
Shard / Mask
避免資料外洩
三、你這個架構的「商用優勢」
你能控制品質
你能控制法規風險
你能隨時切回中心化 GPU
代幣只是工具，不是商品
這是很多 Web3 專案做不到的。
四、下一步最關鍵的實作順序（建議）
接下來你「一定要先做」的是：
GPU Agent 任務流程定義
推論任務驗證邏輯
代幣結算模型
      
