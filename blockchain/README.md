# Blockchain Settlement Layer

## 功能說明

區塊鏈結算層負責：
- VCoin 智能合約管理
- Coin 鑄造與銷毀
- 質押與 Slashing
- 獎勵分配記錄

## 技術選型

### 方案 A: 基於現有 EVM 鏈
- **鏈**: Polygon / Avalanche / BSC
- **語言**: Solidity
- **開發框架**: Hardhat / Foundry

### 方案 B: 自建 Layer 1
- **框架**: Cosmos SDK / Substrate
- **語言**: Go / Rust
- **共識**: Tendermint / BABE+GRANDPA

## 智能合約

### VCoin.sol
主要 Token 合約，實現：
- ERC20 標準介面
- 鑄造權限控制（僅平台）
- 質押與 Slashing 機制
- 燃燒功能

### Governance.sol（Phase 3）
治理合約，實現：
- 提案建立
- 投票機制
- 提案執行

## 部署指南

```bash
# 1. 安裝依賴
npm install

# 2. 配置環境變數
cp .env.example .env
# 編輯 .env，填入 RPC URL、私鑰等

# 3. 編譯合約
npx hardhat compile

# 4. 部署至 Testnet
npx hardhat run scripts/deploy.js --network mumbai

# 5. 驗證合約
npx hardhat verify --network mumbai DEPLOYED_ADDRESS
```

## 合約地址（Testnet）

- **VCoin**: TBD
- **Governance**: TBD

## 安全審計

智能合約在主網部署前需經過：
1. 內部代碼審查
2. 第三方安全審計
3. Bug Bounty 計畫

## 開發指南

詳見 [開發實作指南](../docs/05-開發實作指南.md#22-coin-智能合約)
