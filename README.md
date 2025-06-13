# 🎵🔐 批量音视频文件加密/解密工具 (ChaCha20-Poly1305)

一款基于Python的多线程批处理工具，支持主流音视频格式的加密与解密。采用安全认证的ChaCha20-Poly1305算法，结合PBKDF2密码派生，确保数据机密与完整。支持自动文件去重、时间戳保持、交互式操作，操作简单高效。

---

## 🚀 功能亮点

- 🔒 **认证加密**：ChaCha20-Poly1305保证数据的加密安全和完整性  
- 🔑 **强密码派生**：PBKDF2迭代10万次，使用固定盐稳定生成密钥  
- 🗂 **主流格式支持**：自动识别 `.mp3`, `.wav`, `.aac`, `.flac`, `.ogg`, `.mp4`, `.avi`, `.mkv`, `.mov`, `.flv`, `.wmv`  
- ⚙️ **多线程加速**：默认8线程并发，提升处理效率  
- 🔍 **重复文件剔除**：基于SHA256文件哈希去重，避免重复加密/解密  
- ⏰ **时间戳保持**：操作后文件访问和修改时间保持不变  
- 💬 **交互式命令行**：无需命令行参数，操作友好  

---

## 🧑‍💻 使用指南

1. 克隆仓库或下载源码：
    ```bash
    git clone https://github.com/wangyifan349/encrypt.git
    cd encrypt
    ```

2. 安装依赖：
    ```bash
    pip install pycryptodome
    ```

3. 运行程序：
    ```bash
    python main.py
    ```

4. 按提示输入：
    - 根目录路径（程序将递归扫描处理该目录下所有符合条件的文件）
    - 操作模式：`encrypt`（加密）或 `decrypt`（解密）
    - 密码（用于派生加密密钥）

示例交互：

```
Please enter the root directory path: /your/media/folder
Please choose the operation mode (encrypt / decrypt): encrypt
Please enter the password: mySecretPassword123
```

---

## 🗃️ 去重机制详解

- 程序会对所有目标文件计算SHA256哈希值，找出重复文件  
- 同内容文件只处理首次出现的那个，减少无效重复工作  
- 日志会提示跳过的重复文件路径，方便核查  

---

## 📂 支持文件格式

- **音频**: `.mp3`, `.wav`, `.aac`, `.flac`, `.ogg`  
- **视频**: `.mp4`, `.avi`, `.mkv`, `.mov`, `.flv`, `.wmv`  

---

## 📁 目录结构

- `main.py` — 主程序文件，包含所有功能实现  

---

## 🙋‍♂️ 联系与反馈

欢迎在 GitHub 主页留言或Issues提交建议：

[https://github.com/wangyifan349](https://github.com/wangyifan349)

---

感谢使用！祝你数据安全，管理高效！🎉🔐

如果你希望加上更详细操作
