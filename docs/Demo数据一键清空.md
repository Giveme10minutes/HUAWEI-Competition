# Demo 数据一键清空

录制新一轮视频前，双击项目根目录的 `清空Demo数据.command`。窗口显示“清空完成”后刷新网页，按回车关闭终端窗口。

双击即执行清空，不会二次询问。请在当前回复结束后操作，清空期间不要继续发送消息或保存记录。

命令行也可以运行：

```sh
.venv/bin/python scripts/reset_demo_data.py --yes
```

只查看记录数量：

```sh
.venv/bin/python scripts/reset_demo_data.py --dry-run
```

默认读取项目根目录.env中的APP_DB_PATH，未设置则使用local_data/app.sqlite3。无需重启后端。清除全部对话（含软删除）、消息、个人线索、规划版本及其中行动；保留表结构、.env、API配置、代码、知识资料和历史备份。不清理云端会话历史，但清空后新建对话使用新ID。

没有--yes且在交互终端运行时，需要输入CLEAR；非交互运行必须显式带--yes。脚本拒绝未知业务表结构、缺失数据库和有pending消息的数据库；删除和空状态验证在同一SQLite事务内完成。API读取空规划时可能自动创建空的规划容器，这不是残留业务记录。

验证：只用临时SQLite测试清空/重复清空、结构保留、dry-run、pending阻止、未知表和缺失文件不修改。创建脚本时对当前数据库仅执行dry-run，未清空现有录制内容。
