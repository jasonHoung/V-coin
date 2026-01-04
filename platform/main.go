package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/google/uuid"
	"github.com/gorilla/mux"
)

// Task 任務結構
type Task struct {
	ID         string                 `json:"id"`
	UserID     string                 `json:"user_id"`
	Type       string                 `json:"type"`
	ModelID    string                 `json:"model_id"`
	Input      string                 `json:"input"`
	Parameters map[string]interface{} `json:"parameters,omitempty"`
	Status     string                 `json:"status"`
	Result     string                 `json:"result,omitempty"`
	NodeID     string                 `json:"node_id,omitempty"`
	CreatedAt  time.Time              `json:"created_at"`
}

// InferenceRequest 推論請求
type InferenceRequest struct {
	ModelID    string                 `json:"model_id"`
	Input      string                 `json:"input"`
	Parameters map[string]interface{} `json:"parameters,omitempty"`
}

// Node 節點結構
type Node struct {
	ID             string    `json:"id"`
	GPUModel       string    `json:"gpu_model"`
	GPUMemory      int       `json:"gpu_memory"`
	Status         string    `json:"status"`
	ReputationScore float64   `json:"reputation_score"`
	LastHeartbeat  time.Time `json:"last_heartbeat"`
}

// HeartbeatRequest 心跳請求
type HeartbeatRequest struct {
	NodeID         string  `json:"node_id"`
	GPUModel       string  `json:"gpu_model"`
	GPUMemory      int     `json:"gpu_memory"`
	GPUUtilization float64 `json:"gpu_utilization"`
	Temperature    float64 `json:"temperature"`
	Status         string  `json:"status"`
}

// 簡單的記憶體儲存（實際應使用資料庫）
var (
	tasks = make(map[string]*Task)
	nodes = make(map[string]*Node)
)

func main() {
	router := mux.NewRouter()

	// API 路由
	router.HandleFunc("/api/v1/inference", createInferenceHandler).Methods("POST")
	router.HandleFunc("/api/v1/task/{id}/status", getTaskStatusHandler).Methods("GET")
	router.HandleFunc("/api/v1/node/heartbeat", heartbeatHandler).Methods("POST")
	router.HandleFunc("/api/v1/node/{id}/task", getNodeTaskHandler).Methods("GET")

	// 健康檢查
	router.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
	})

	fmt.Println("🚀 V-Coin Platform Server 啟動於 :8080")
	log.Fatal(http.ListenAndServe(":8080", router))
}

// createInferenceHandler 建立推論任務
func createInferenceHandler(w http.ResponseWriter, r *http.Request) {
	var req InferenceRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	task := &Task{
		ID:         uuid.New().String(),
		UserID:     "test-user", // 測試用
		Type:       "inference",
		ModelID:    req.ModelID,
		Input:      req.Input,
		Parameters: req.Parameters,
		Status:     "pending",
		CreatedAt:  time.Now(),
	}

	tasks[task.ID] = task

	fmt.Printf("✅ 建立任務: %s (Model: %s)\n", task.ID, task.ModelID)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(task)
}

// getTaskStatusHandler 查詢任務狀態
func getTaskStatusHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	taskID := vars["id"]

	task, exists := tasks[taskID]
	if !exists {
		http.Error(w, "Task not found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(task)
}

// heartbeatHandler 處理節點心跳
func heartbeatHandler(w http.ResponseWriter, r *http.Request) {
	var req HeartbeatRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	node, exists := nodes[req.NodeID]
	if !exists {
		// 新節點註冊
		node = &Node{
			ID:              req.NodeID,
			GPUModel:        req.GPUModel,
			GPUMemory:       req.GPUMemory,
			Status:          req.Status,
			ReputationScore: 100.0,
		}
		nodes[req.NodeID] = node
		fmt.Printf("🆕 新節點註冊: %s (%s)\n", node.ID, node.GPUModel)
	}

	node.LastHeartbeat = time.Now()
	node.Status = req.Status

	// 檢查是否有待處理任務
	hasTask := false
	for _, task := range tasks {
		if task.Status == "pending" {
			hasTask = true
			break
		}
	}

	response := map[string]interface{}{
		"status":   "ok",
		"has_task": hasTask,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// getNodeTaskHandler 節點獲取任務
func getNodeTaskHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	nodeID := vars["id"]

	node, exists := nodes[nodeID]
	if !exists {
		http.Error(w, "Node not found", http.StatusNotFound)
		return
	}

	// 找到第一個待處理任務
	var assignedTask *Task
	for _, task := range tasks {
		if task.Status == "pending" {
			task.Status = "running"
			task.NodeID = nodeID
			assignedTask = task
			fmt.Printf("📋 分配任務 %s 給節點 %s\n", task.ID, nodeID)
			break
		}
	}

	if assignedTask == nil {
		http.Error(w, "No tasks available", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(assignedTask)
}
