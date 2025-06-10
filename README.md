# Modbus RTU 温度采集系统

这是一个使用 Python 和 modbus_tk 库实现的 Modbus RTU 温度采集演示程序。

## 功能特性

- 通过串口与 Modbus RTU 设备通信
- 实时读取温度传感器数据
- 每秒输出一次温度值到控制台
- 支持温度超标报警
- 完整的错误处理和日志记录

## 系统要求

- Python 3.6+
- Windows 10 / macOS / Linux
- 串口设备（USB转串口或内置串口）

## 安装依赖

```bash
# 安装项目依赖
pip install -r requirements.txt

# 或者手动安装
pip install modbus_tk pyserial
```

## 配置说明

在运行程序前，请根据您的实际设备配置修改 `modbus_reader.py` 中的参数：

```python
# 主要配置参数
PORT = 'COM2'        # Windows: COM1, COM2 等; Linux/Mac: /dev/ttyUSB0 等
BAUDRATE = 38400     # 波特率，常见值：9600, 19200, 38400, 115200
SLAVE_ID = 1         # Modbus 从站地址
INTERVAL = 1         # 读取间隔（秒）
```

## 使用方法

### 1. 基本运行

```bash
python modbus_reader.py
```

### 2. 预期输出

```
============================================================
Modbus RTU 温度采集系统
============================================================
2024-01-01 10:00:00,123 - INFO - 初始化Modbus客户端: 端口=COM2, 波特率=38400, 从站=1
2024-01-01 10:00:00,456 - INFO - Modbus设备连接成功
2024-01-01 10:00:00,789 - INFO - 开始温度监控，读取间隔: 1秒
2024-01-01 10:00:00,790 - INFO - 按 Ctrl+C 停止监控

[2024-01-01 10:00:01] 温度数据读取:
原始寄存器值: [250, 251, 255, 260, 245, 248, 252, 258, 249, 253, 256, 247]
解析温度值: ['25.0°C', '25.1°C', '25.5°C', '26.0°C', '24.5°C', '24.8°C', '25.2°C', '25.8°C', '24.9°C', '25.3°C', '25.6°C', '24.7°C']

[2024-01-01 10:00:02] 温度数据读取:
原始寄存器值: [251, 252, 256, 261, 246, 249, 253, 259, 250, 254, 257, 248]
解析温度值: ['25.1°C', '25.2°C', '25.6°C', '26.1°C', '24.6°C', '24.9°C', '25.3°C', '25.9°C', '25.0°C', '25.4°C', '25.7°C', '24.8°C']
```

### 3. 停止程序

按 `Ctrl+C` 停止监控程序。

## Modbus 配置说明

### 寄存器映射

| 寄存器地址 | 数据类型 | 说明 |
|------------|----------|------|
| 0-11 | 保持寄存器 | 12个温度传感器值 |

### 数据格式

- **原始格式**: 16位整数（例如：250 表示 25.0°C）
- **解析方式**: 寄存器值除以10得到实际温度
- **精度**: 0.1°C

### 通信参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 协议 | Modbus RTU | 串口通信协议 |
| 功能码 | 03 | 读保持寄存器 |
| 数据位 | 8 | 串口数据位 |
| 校验位 | None | 无校验 |
| 停止位 | 1 | 串口停止位 |
| 超时 | 1秒 | 通信超时时间 |

## 故障排除

### 常见问题

1. **连接失败**
   ```
   错误: 连接异常: could not open port 'COM2'
   解决: 检查串口号是否正确，设备是否已连接
   ```

2. **权限错误**（Linux/Mac）
   ```bash
   # 添加用户到串口组
   sudo usermod -a -G dialout $USER
   # 或临时修改权限
   sudo chmod 666 /dev/ttyUSB0
   ```

3. **读取超时**
   ```
   错误: 读取温度数据异常: Modbus Error
   解决: 检查设备地址、波特率、功能码是否正确
   ```

### 调试模式

修改日志级别以获取更详细的调试信息：

```python
# 在 modbus_reader.py 中修改
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## 扩展功能

### 1. 数据记录

```python
# 添加到温度读取循环中
import csv
from datetime import datetime

# 保存到CSV文件
with open('temperature_log.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([datetime.now()] + temperatures)
```

### 2. 报警通知

```python
# 邮件报警示例
import smtplib
from email.mime.text import MIMEText

def send_alert(sensor_id, temperature):
    msg = MIMEText(f'传感器{sensor_id}温度异常: {temperature}°C')
    # 配置邮件服务器并发送
```

### 3. Web界面

可以集成 Flask 或 FastAPI 创建 Web 监控界面。

## 许可证

MIT License

## 技术支持

如有问题，请检查：
1. 硬件连接是否正确
2. 串口参数是否匹配
3. Modbus 设备配置是否正确
4. Python 依赖是否正确安装