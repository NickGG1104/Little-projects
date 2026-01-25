### Create Modelfile
```dockerfile
# 指定 GGUF 檔案路徑
FROM "/Users/yisen/Desktop/Resource/Coding/Python/Project/Agent Skills/Models/llama-3-taiwan-8B-instruct-q4_k_m.gguf"

# 設定對話模板
TEMPLATE """{{ if .System }}<|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|>{{ end }}{{ if .Prompt }}<|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|>{{ end }}<|start_header_id|>assistant<|end_header_id|>

{{ .Response }}<|eot_id|>"""

# 設定參數
PARAMETER temperature 0.2
PARAMETER num_ctx 4096
PARAMETER stop "<|eot_id|>"
```

### Create Model
```cmd
ollama create llama3-tw -f "/Users/yisen/Desktop/Resource/Coding/Python/Project/Agent Skills/Models/Modelfile"
```

### Setting
```cmd
OLLAMA_NUM_PARALLEL=4      # 同時服務 4 個人
OLLAMA_NUM_CTX=8192        # 給每個人超大的 8k 記憶視窗 (處理長SOP很好用)
OLLAMA_KEEP_ALIVE=24h
```