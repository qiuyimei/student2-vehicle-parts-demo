# 09 GitHub与成果交付

本项目仓库为[qiuyimei/student2-vehicle-parts-demo](https://github.com/qiuyimei/student2-vehicle-parts-demo)。本章说明怎样理解仓库、保存实验、提交变化与取得完整材料。

## 第一步 认识仓库与Release

仓库的Code页面保存源码、教程、示例和已登记的结果。Release保存离线源码与Demo包、模型和整理后的10类数据包。二者用途不同，但都属于同一个项目的交付。

133MB数据包超过GitHub常规Git单文件100MiB限制，因此通过[Release](https://github.com/qiuyimei/student2-vehicle-parts-demo/releases/latest)提供，不直接塞入Git历史。限制依据[GitHub官方说明](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)。从Git克隆时，模型由下载脚本准备；Release的离线源码包则包含已校验权重。

## 第二步 检查当前本地版本

在通过Git克隆的工程目录执行：

```powershell
git status
git remote -v
git log --oneline -5
```

`status`列出本地变化，`remote`应指向本项目，`log`展示提交。直接解压ZIP得到的目录没有`.git`，不能把“not a git repository”当成源码丢失；需要用Git克隆才能按本章提交。

## 第三步 为一项工作建立分支

```powershell
git switch -c improve/part-label-notes
```

这个分支名只是一次练习示例。每个分支集中解决一个问题，例如“补充侧别标注说明”或“增加跨部件测试”，便于复查变化与回退。

## 第四步 修改后先看差异

```powershell
git status --short
git diff -- docs/部件标注规范.md
```

确认修改的确是本次要保存的内容。模型、数据与服务日志默认被忽略；这不是文件消失，而是`.gitignore`避免把可重新获取的大文件和本机运行状态混进源码提交。

## 第五步 执行与修改相关的检查

改教程后运行：

```powershell
& .\.venv\Scripts\python.exe scripts/check_docs.py
```

改算法后运行对应测试；准备正式提交时再执行全部测试：

```powershell
& .\.venv\Scripts\python.exe -m pytest -q
```

若改变模型或参数，要另存新结果并记录条件，不应把旧模型的精度报告改成新实验的名称。

## 第六步 显式选择要提交的文件

```powershell
git add docs/部件标注规范.md
git diff --cached --stat
git diff --cached
git commit -m 'Clarify left and right part annotation rules'
git push -u origin improve/part-label-notes
```

上面的命令假定你确实修改了该文件。若没有修改，不要为了演示提交而制造空改动。提交信息应说明真实变化，而不是只写“更新”。

本地`git commit`只保存在电脑上；`git push`才把分支上传到GitHub。失败时检查账号、访问权限和网络，不要把失败输出删掉后宣称已上传。

## 第七步 在GitHub查看检查与变化

推送后查看分支的Commits和Files Changed。仓库的Actions运行轻量匹配与归档测试，不运行全部模型与数据精度验证。绿色检查只证明工作流中的断言通过，不能替代人工查看预测图片。

如采用Pull Request协作，在说明中写清问题、改动、验证命令与结果。另一个成员可以根据差异复查后再合并。

## 第八步 保存个人成果证据

建议提交能够解释个人工作的内容：部件类别表、数据转换脚本、模型复现命令、匹配公式与边界处理、接口样例、测试记录和真实失败案例。原始公开模型来源应继续保留。

不要把“下载了一个模型文件”写成“完成模型训练”；不要把复制公开标注写成“新采集并人工标注”；也不要用自动匹配数量充当关联准确率。

## 第九步 发布一个可复现版本

发布前保存提交ID、检查测试和教程链接，再给版本打标签。例如未来某个实际版本可以使用新的tag；不要反复移动已经发布的标签。

Release说明应包含：版本对应的提交、运行方式、源码包与数据包用途、文件SHA256、已完成与未执行的实验。接收者先核对校验值，再按教程复现。

## 第十步 交付时的最小材料

| 材料 | 接收者用它做什么 |
| --- | --- |
| 仓库链接与版本号 | 找到正确源码和教程 |
| 标注规范与类别映射 | 理解部件名称与标签 |
| 模型来源和SHA256 | 使用同一份权重 |
| 启动与联调命令 | 真正运行个人模块 |
| 测试和实验原始结果 | 复核结论，而不只看截图 |
| 至少一个失败案例 | 理解方法的实际限制 |

本章验收：能区分commit、push与Release；知道哪些大文件在Release；提交记录能追溯到自己的改动与验证。

下一步：[10 常见问题逐项排查](10-常见问题逐项排查.md)。
