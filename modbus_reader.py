#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modbus RTU 温度采集模块通信程序
功能：通过串口读取Modbus设备的温度数据，每秒输出一次
作者：Demo
日期：2024
"""

import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import serial
import time
import logging
import sys

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class ModbusTemperatureReader:
    """
    Modbus RTU 温度读取器类
    """
    
    def __init__(self, port='COM2', baudrate=38400, slave_id=1):
        """
        初始化Modbus客户端
        
        Args:
            port (str): 串口号，默认COM2
            baudrate (int): 波特率，默认38400
            slave_id (int): 从站地址，默认1
        """
        self.port = port
        self.baudrate = baudrate
        self.slave_id = slave_id
        self.master = None
        
        log.info(f"初始化Modbus客户端: 端口={port}, 波特率={baudrate}, 从站={slave_id}")
    
    def connect(self):
        """
        连接到Modbus设备
        
        Returns:
            bool: 连接成功返回True，失败返回False
        """
        try:
            # 创建Modbus RTU主站
            self.master = modbus_rtu.RtuMaster(
                serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    bytesize=8,
                    parity='N',
                    stopbits=1,
                    timeout=1
                )
            )
            self.master.set_timeout(1.0)
            self.master.set_verbose(True)
            log.info("Modbus设备连接成功")
            return True
        except Exception as e:
            log.error(f"连接异常: {str(e)}")
            return False
    
    def disconnect(self):
        """
        断开Modbus连接
        """
        try:
            if self.master:
                self.master.close()
                log.info("Modbus连接已断开")
        except Exception as e:
            log.error(f"断开连接异常: {str(e)}")
    
    def read_temperatures(self, start_address=0, count=12):
        """
        读取温度寄存器数据
        
        Args:
            start_address (int): 起始寄存器地址，默认0
            count (int): 读取寄存器数量，默认12
            
        Returns:
            list: 温度数据列表，读取失败返回空列表
        """
        try:
            if not self.master:
                log.error("Modbus主站未初始化")
                return []
            
            # 读取保持寄存器（功能码03）
            registers = self.master.execute(
                self.slave_id,
                cst.READ_HOLDING_REGISTERS,
                start_address,
                count
            )
            
            log.debug(f"读取到{len(registers)}个寄存器值: {registers}")
            return list(registers)
            
        except Exception as e:
            log.error(f"读取温度数据异常: {str(e)}")
            return []
    
    def parse_temperatures(self, registers):
        """
        解析温度数据（可根据实际设备调整解析方式）
        
        Args:
            registers (list): 原始寄存器值列表
            
        Returns:
            list: 解析后的温度值列表
        """
        if not registers:
            return []
        
        # 方案1：假设温度值为10倍精度整数（常见格式）
        # 例如：寄存器值250表示25.0°C
        temperatures = [reg / 10.0 for reg in registers]
        
        # 方案2：如果是32位浮点数格式（每2个寄存器组成1个温度值）
        # import struct
        # temperatures = []
        # for i in range(0, len(registers), 2):
        #     if i + 1 < len(registers):
        #         packed = struct.pack('>HH', registers[i], registers[i+1])
        #         temp = struct.unpack('>f', packed)[0]
        #         temperatures.append(temp)
        
        return temperatures
    
    def start_monitoring(self, interval=1):
        """
        开始温度监控循环
        
        Args:
            interval (int): 读取间隔时间（秒），默认1秒
        """
        log.info(f"开始温度监控，读取间隔: {interval}秒")
        log.info("按 Ctrl+C 停止监控")
        
        try:
            while True:
                # 读取原始寄存器值
                raw_data = self.read_temperatures()
                
                if raw_data:
                    # 解析温度值
                    temperatures = self.parse_temperatures(raw_data)
                    
                    # 格式化输出
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    print(f"\n[{timestamp}] 温度数据读取:")
                    print(f"原始寄存器值: {raw_data}")
                    print(f"解析温度值: {[f'{temp:.1f}°C' for temp in temperatures]}")
                    
                    # 检查异常温度（可选）
                    self.check_temperature_alerts(temperatures)
                else:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 温度数据读取失败")
                
                # 等待下次读取
                time.sleep(interval)
                
        except KeyboardInterrupt:
            log.info("\n用户中断，停止监控")
        except Exception as e:
            log.error(f"监控过程异常: {str(e)}")
        finally:
            self.disconnect()
    
    def check_temperature_alerts(self, temperatures, threshold=30.0):
        """
        检查温度报警
        
        Args:
            temperatures (list): 温度值列表
            threshold (float): 报警阈值，默认30.0°C
        """
        for i, temp in enumerate(temperatures):
            if temp > threshold:
                print(f"⚠️  警报！传感器{i+1}温度超标: {temp:.1f}°C (阈值: {threshold}°C)")


def main():
    """
    主函数
    """
    print("=" * 60)
    print("Modbus RTU 温度采集系统")
    print("=" * 60)
    
    # 配置参数（可根据实际情况修改）
    PORT = 'COM2'        # Windows系统串口号，Mac/Linux可能是'/dev/ttyUSB0'等
    BAUDRATE = 38400     # 波特率
    SLAVE_ID = 1         # 从站地址
    INTERVAL = 1         # 读取间隔（秒）
    
    # 创建温度读取器
    reader = ModbusTemperatureReader(port=PORT, baudrate=BAUDRATE, slave_id=SLAVE_ID)
    
    # 尝试连接设备
    if reader.connect():
        # 开始监控
        reader.start_monitoring(interval=INTERVAL)
    else:
        print("无法连接到Modbus设备，请检查：")
        print("1. 串口号是否正确")
        print("2. 设备是否已连接并开启")
        print("3. 串口参数是否匹配")
        print("4. 是否有其他程序占用串口")
        sys.exit(1)


if __name__ == "__main__":
    main()