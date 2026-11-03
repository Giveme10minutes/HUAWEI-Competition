# Go（golang）

资料ID：RM-P02-GOLANG ｜ 批次：RM-P02 ｜ 版本 v0.2 ｜ 整理日期：2026-11-03
类型：语言 ｜ 所属：后端 ｜ 对应仓库路线：`roadmaps/golang`

## 1. 定位

并发与云原生场景常用语言。

## 2. 学习阶段

### 阶段 1：语法与核心概念

- 语法、类型、控制流、函数与错误处理
- 标准库中最常用的部分
- 调试与最小可运行程序

### 阶段 2：常见用法

- 用该语言完成一个真实小项目
- 常用第三方库与项目结构
- 读写文件、网络请求等常见任务

### 阶段 3：工程化

- 测试、依赖管理与构建
- 性能与内存等该语言的典型问题
- 代码规范与团队协作

## 3. 主题清单（检索用）

以下名称取自本地仓库 `roadmaps/golang/content/` 的文件标题，共 **172** 个去重主题；仅作覆盖面参考，不代表必须全部学完。

| 主题 | 文件标识 |
| --- | --- |
| Anonymous Functions | `anonymous-functions` |
| Array to Slice Conversion | `array-to-slice-conversion` |
| Arrays | `arrays` |
| beego | `beego` |
| Benchmarks | `benchmarks` |
| Boolean | `boolean` |
| break | `break` |
| bubbletea | `bubbletea` |
| Buffered vs Unbuffered | `buffered-vs-unbuffered` |
| bufio | `bufio` |
| Build Constraints & Tags | `build-constraints--tags` |
| Build Tags | `build-tags` |
| Building CLIs | `building-clis` |
| Building Executables | `building-executables` |
| Call by Value | `call-by-value` |
| Capacity and Growth | `capacity-and-growth` |
| Centrifugo | `centrifugo` |
| CGO Basics | `cgo-basics` |
| Channels | `channels` |
| Closures | `closures` |
| Cobra | `cobra` |
| Comma-Ok Idiom | `comma-ok-idiom` |
| Commands & Docs | `commands--docs` |
| Common Usecases | `common-usecases` |
| Compiler & Linker Flags | `compiler--linker-flags` |
| Complex Numbers | `complex-numbers` |
| Concurrency Patterns | `concurrency-patterns` |
| Conditionals | `conditionals` |
| const and iota | `const-and-iota` |
| context package | `context-package` |
| continue | `continue` |
| Coverage | `coverage` |
| Cross-compilation | `cross-compilation` |
| Data Types | `data-types` |
| Deadlines & Cancellations | `deadlines--cancellations` |
| echo | `echo` |
| Embedding Interfaces | `embedding-interfaces` |
| Embedding Structs | `embedding-structs` |
| Empty Interface | `empty-interfaces` |
| Encoding / JSON | `encodingjson` |
| Error Handling Basics | `error-handling-basics` |
| error interface | `error-interface` |
| errors.New | `errorsnew` |
| Escape Analysis | `escape-analysis` |
| Fan-in | `fan-in` |
| Fan-out | `fan-out` |
| fiber | `fiber` |
| flag | `flag` |
| Floating Points | `floating-points` |
| fmt.Errorf | `fmterrorf` |
| for loop | `for-loop` |
| for-range | `for-range` |
| Function Basics | `functions-basics` |
| Functions | `functions` |
| Garbage Collection | `garbage-collection` |
| Generic Functions | `generic-functions` |
| Generic Types / Interfaces | `generic-types--interfaces` |
| Generics | `generics` |
| gin | `gin` |
| go build | `go-build` |
| go clean | `go-clean` |
| go command | `go-command` |
| go doc | `go-doc` |
| go fmt | `go-fmt` |
| go generate | `go-generate` |
| go install | `go-install` |
| go mod init | `go-mod-init` |
| go mod tidy | `go-mod-tidy` |
| go mod vendor | `go-mod-vendor` |
| go mod | `go-mod` |
| go run | `go-run` |
| go test | `go-test` |
| go version | `go-version` |
| go vet | `go-vet` |
| go:embed for embedding | `goembed-for-embedding` |
| goimports | `goimports` |
| golangci-lint | `golangci-lint` |
| GORM | `gorm` |
| Goroutines | `goroutines` |
| goto (discouraged) | `goto-discouraged` |
| govulncheck | `govulncheck` |
| gRPC & Protocol Buffers | `grpc--protocol-buffers` |
| Hello World in Go | `hello-world-in-go` |
| History of Go | `history-of-go` |
| httptest for HTTP Tests | `httptest--for-http-tests` |
| if-else | `if-else` |
| if | `if` |
| Integers (Signed, Unsigned) | `integers-signed-unsigned` |
| Interfaces Basics | `interfaces-basics` |
| Interfaces | `interfaces` |
| Interpreted String Literals | `interpreted-string-literals` |
| Introduction to Go | `introduction-to-go` |
| I/O & File Handling | `io--file-handling` |
| Iterating Maps | `iterating-maps` |
| Iterating Strings | `iterating-strings` |
| Logging | `logging` |
| Loops | `loops` |
| make() | `make` |
| Maps | `maps` |
| Melody | `melody` |
| Memory Management | `memory-management` |
| Memory Management in Depth | `memory-mgmt-in-depth` |
| Methods vs Functions | `methods-vs-functions` |
| Mocks and Stubs | `mocks-and-stubs` |
| Modules & Dependencies | `modules--dependencies` |
| Multiple Return Values | `multiple-return-values` |
| Mutexes | `mutexes` |
| Named Return Values | `named-return-values` |
| net/http Standard | `nethttp-standard` |
| ORMs & DB Access | `orms--db-access` |
| os | `os` |
| Package Import Rules | `package-import-rules` |
| Packages | `packages` |
| panic and recover | `panic-and-recover` |
| pgx | `pgx` |
| Pipeline | `pipeline` |
| Plugins & Dynamic Loading | `plugins--dynamic-loading` |
| Pointer Receivers | `pointer-receivers` |
| Pointer Basics | `pointers-basics` |
| Pointers with Structs | `pointers-with-structs` |
| （其余 52 个略） | — |

## 4. 与相邻内容的关系

- 它是“后端”方向常用的语言/框架，不是独立职业方向；先有方向目标再选它更稳。
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
