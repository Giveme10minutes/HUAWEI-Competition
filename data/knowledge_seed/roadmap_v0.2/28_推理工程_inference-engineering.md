# 推理工程（inference-engineering）

资料ID：RM-P02-INFERENCE_ENGINEERING ｜ 批次：RM-P02 ｜ 版本 v0.2 ｜ 整理日期：2026-11-03
类型：新兴/专项 ｜ 所属：AI ｜ 对应仓库路线：`roadmaps/inference-engineering`

## 1. 定位

把模型推理做得更快、更省资源。

## 2. 学习阶段

### 阶段 1：概念与边界

- 它解决什么问题，不解决什么问题
- 与相邻概念的区别
- 常见术语

### 阶段 2：典型工作流

- 跑通一个最小可用流程
- 评估效果与失败样例
- 成本、延迟与风险

### 阶段 3：评估与落地

- 建立评测方法
- 在真实约束下迭代
- 写清局限与适用条件

## 3. 主题清单（检索用）

以下名称取自本地仓库 `roadmaps/inference-engineering/content/` 的文件标题，共 **140** 个去重主题；仅作覆盖面参考，不代表必须全部学完。

| 主题 | 文件标识 |
| --- | --- |
| AI-Native Applications | `ai-native-applications` |
| NVIDIA GenAI-Perf | `aiperf` |
| Arithmetic Intensity | `arithmetic-intensity` |
| Asynchronous Inference | `asynchronous-inference` |
| Attention Mechanism | `attention-mechanism` |
| Attention Optimization | `attention-optimization` |
| Attention Variants | `attention-variants` |
| Automatic Speech Recognition (ASR) | `auto-speech-recognition` |
| Autoscaling | `autoscaling` |
| Benchmarking and Profiling | `benchmarking--profiling` |
| BERT-style Models | `bert-style-models` |
| Blackwell | `blackwell` |
| Bottleneck Analysis | `bottleneck-analysis` |
| Cache-Aware Routing | `cache-aware-routing` |
| Caching Approaches | `caching-approaches` |
| Caching | `caching` |
| Capacity Management | `capacity-management` |
| Client Integration | `client-integration` |
| Client Latency Overhead | `client-latency-overhead` |
| Cold Starts | `cold-starts` |
| Compute | `compute` |
| Constrained Decoding | `constrained-decoding` |
| Consumer vs. B2B Workloads | `consumer-vs-b2b` |
| Containerization | `containerization` |
| Continuous Batching | `continuous-batching` |
| Cost Estimation | `cost-estimation` |
| CUDA | `cuda` |
| Dependency Management | `dependency-management` |
| Desktop Inference | `desktop-inference` |
| Diffusion Models | `diffusion-models` |
| Disaggregation | `disaggregation` |
| Distillation | `distillation` |
| Draft-Target Speculative Decoding | `draft-target-decoding` |
| EAGLE | `eagle` |
| Embedding Model Inference | `embedding-model-inference` |
| Embedding Models | `embedding-models` |
| Encoder-Decoder Architectures | `encoder-decoder-arch` |
| End-to-End Metrics | `end-to-end-metrics` |
| Expert Parallelism | `expert-parallelism` |
| Few-Step Image Generation | `few-step-image-generation` |
| Fine-Tuning | `fine-tuning` |
| FlashAttention | `flashattention` |
| Frameworks and Libraries | `frameworks--libraries` |
| Geo-Aware Load Balancing | `geo-aware-load-balancing` |
| GPU Architecture | `gpu-architecture` |
| GPU Models | `gpu-models` |
| GPU Procurement | `gpu-procurement` |
| Grace and Vera CPUs | `grace--vera` |
| Hopper | `hopper` |
| Image and Video Generation Bottlenecks | `image--video-bottlenecks` |
| Image and Video Generation | `image--video-generation` |
| Image & Video Models | `image--video-models` |
| Image Generation Architecture | `image-generation-arch` |
| Image Generation Inference | `image-generation-inference` |
| Independent Component Scaling | `indep-component-scaling` |
| Inference Engines | `inference-engines` |
| Inference vs. Training | `inference-vs-training` |
| Instances and Interconnects | `instances--interconnects` |
| Inter-Token Latency (ITL) | `inter-token-latency` |
| Inference Engineer | `introduction` |
| Kernel Selection and Fusion | `kernel-selection--fusion` |
| KV Cache Storage | `kv-cache-storage` |
| KV Cache | `kv-cache` |
| Large Language Models | `large-language-models` |
| Latency Percentiles | `latency-percentiles` |
| Latency vs. Throughput | `latency-vs-throughput` |
| LLM-based Models | `llm-based-models` |
| LLM Inference Bottlenecks | `llm-bottlenecks` |
| Local and Edge Inference | `local--edge-inference` |
| Locust | `locust` |
| Long Context Handling | `long-context-handling` |
| LoRA-Aware Routing | `lora-aware-routing` |
| Measuring Quality Impact | `measuring-quality-impact` |
| Memory | `memory` |
| Mixture of Experts (MoE) | `mixture-of-experts-moe` |
| Mobile Inference | `mobile-inference` |
| Model Evaluation | `model-evaluation` |
| Model Formats and Runtimes | `model-formats--runtimes` |
| Model Parallelism | `model-parallelism` |
| Model Selection | `model-selection` |
| ModelOpt | `modelopt` |
| Multi-Cloud | `multi-cloud` |
| Multi-Node Inference | `multi-node-inference` |
| N-gram Speculation | `n-gram` |
| Neural Networks | `neural-networks` |
| NIMs | `nims` |
| NVIDIA Dynamo | `nvidia-dynamo` |
| NVIDIA | `nvidia` |
| Observability | `observability` |
| Omni-Modal Models | `omni-modal-models` |
| Online vs. Offline Inference | `online-vs-offline-inf` |
| ONNX Runtime | `onnx-runtime` |
| Open vs. Closed Models | `open-vs-closed-models` |
| Ops:Byte Ratio | `opsbyte-ratio` |
| Other Accelerators | `other-accelerators` |
| PagedAttention | `pagedattention` |
| Performance Benchmarking | `performance-benchmarking` |
| Pipeline Parallelism | `pipeline-parallelism` |
| Post-Training Quantization | `post-training-quantization` |
| Prefill and Decode Phases | `prefill--decode-phases` |
| Profiling Performance | `profiling-performance` |
| PyTorch | `pytorch` |
| Quantization-Aware Training | `quantization-aware-training` |
| Quantization | `quantization` |
| Real-Time Factor (RTF) | `real-time-factor` |
| Reasoning Models | `reasoning-models` |
| Request Queueing | `request-queueing` |
| Roofline Model | `roofline-model` |
| Routing and Load Balancing | `routing--load-balancing` |
| Safetensors | `safetensors` |
| Scale to Zero | `scale-to-zero` |
| Security and Compliance | `security-and-compliance` |
| SGLang Genai-bench | `sglang-genai-bench` |
| SGLang | `sglang` |
| Shared vs. Dedicated Inference | `shared-vs-dedicated-inf` |
| Sizing and Procurement | `sizing--procurement` |
| Speculative Decoding | `speculative-decoding` |
| Speech-to-Speech Models | `speech-to-speech-models` |
| Speech | `speech` |
| Streaming and Protocol Support | `streaming--protocol-support` |
| （其余 20 个略） | — |

## 4. 与相邻内容的关系

- 它属于“AI”下的新兴/专项内容，边界和工具仍在变化。
- 方向地图与区分方法见 `../roadmap_v0.1/00_direction_map.md`；岗位原文条件见 `../computing_pilot_v0.1/`（两者不能互相替代）。

## 5. 本页不包含

- 学时、周数、薪资、就业率与前景判断；
- 具体资源链接、课程与书籍推荐；
- “适合什么人”的适配结论；
- 招聘要求；某方向是否好就业需查岗位原文与市场数据，本页不提供。

## 6. 来源、编排与限制

- 主题名称来自 roadmap.sh 内容仓库的本地快照（`/Users/chenyu/Downloads/developer-roadmap-master/roadmaps/`），仅读取文件标题；**未复制**其说明文字、资源链接或图片，也未使用其 URL。
- 定位、阶段划分与顺序、边界说明均为整理者自写编排，不是招聘方要求，也不是唯一正确路径。
- 技术生态变化快，工具名与主题名可能过时；引用时注明整理日期 2026-11-03。
