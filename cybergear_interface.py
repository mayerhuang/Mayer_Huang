import os
import serial
import struct
import time

# 初始化串口


def initialize_serial_port():
    result = os.popen("sudo ls -l /dev/ttyCH341*").read()
    com = result.split()[-1]
    os.system(f"sudo chmod 777 {com}")
    os.system(f"sudo fuser -k {com}")
    ser = serial.Serial(com, 921600, timeout=1)
    ser.write(bytes.fromhex('41 54 2b 41 54 0d 0a'))
    return ser

# 将浮点数转换为字节表示的字符串


def float_to_bytes(f):
    byte_val = struct.pack('<f', f)
    return ' '.join('{:02x}'.format(b) for b in byte_val)

# 将字节转换为对应的命令文本


def bytes_to_text(cmd_x):
    cmd_dict = {
        '00': ' 获取设备 ID', '01': '运控模式电机控制指令', '02': '电机反馈数据',
        # ... 其他命令映射 ...
        '90': '设置参数'
    }
    return cmd_dict.get(cmd_x, cmd_x)  # 返回对应的命令或默认为字节

# 将带空格的字节表示字符串转换为浮点数


def bytes_to_float(byte_str):
    bytes_val = bytes.fromhex(byte_str.replace(' ', ''))
    float_val = struct.unpack('<f', bytes_val)[0]
    return round(float_val, 4)

# 根据输入值转换为对应的字节


def bytes_to_value(value):
    hex_str = "{:04x}".format(value) if not isinstance(value, str) else value
    high_byte = int(hex_str[:2], 16)
    return 123 + (high_byte - 0xDC) // 8

# 将CANID转换为字节


def value_to_bytes(value):
    high_byte = 0xDC + (value - 123) * 8
    return '{:02x} 08'.format(high_byte)

# 提取命令信息


def extract_info(parsed_command):
    return parsed_command[4:6], parsed_command[10:14], parsed_command[14:18], parsed_command[22:30]

# 整数转为反向的十六进制


def int_to_reversed_hex(value):
    hex_str = "{:04x}".format(value)
    return ' '.join([hex_str[i:i+2].upper() for i in range(2, -1, -2)])

# 反转十六进制字节


def reverse_hex_bytes(hex_str):
    return "0x" + hex_str[2:] + hex_str[:2]

# 发送命令到串口


def send_command(ser, can_id, cmd_mode, index, value):
    id_num, index_num = value_to_bytes(can_id), int_to_reversed_hex(index)
    value_num = float_to_bytes(value)
    date = f"41 54 {cmd_mode} 07 eb {id_num} {index_num} 00 00 {value_num} 0d 0a"
    print(f"发送L91指令：{cmd_mode}至CAN{can_id}:索引{index},值{value}")

    try:
        ser.write(bytes.fromhex(date))
        response = ser.readline()
        hex_string = ' '.join([response[i:i+1].hex()
                              for i in range(len(response))])
        cmd_x, can_id_x, index_x, value_x = extract_info(
            hex_string.replace(" ", ""))
        cmd_int, can_id_int = bytes_to_text(cmd_x), bytes_to_value(can_id_x)
        index_int, value_int = reverse_hex_bytes(
            index_x), bytes_to_float(value_x)
        print(
            f"接收内容《类型: {cmd_int} canid: {can_id_int} index: {index_int} value: {value_int}》RX: {hex_string}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return hex_string

# 主函数测试


def main():
    ser = initialize_serial_port()
    print('位置模式')
    ser.write(bytes.fromhex('41 54 90 07 eb fc 08 05 70 00 00 01 00 00 00 0d 0a'))
    response = ser.readline()
    hex_string = ' '.join([response[i:i+1].hex()
                          for i in range(len(response))])
    cmd_x, can_id_x, index_x, value_x = extract_info(
        hex_string.replace(" ", ""))
    cmd_int, can_id_int = bytes_to_text(cmd_x), bytes_to_value(can_id_x)
    index_int, value_int = reverse_hex_bytes(index_x), bytes_to_float(value_x)
    print(
        f"接收内容《类型: {cmd_int} canid: {can_id_int} index: {index_int} value: {value_int}》RX: {hex_string}")
    print('设置模式1')
    send_command(ser,127, '18', 28677, 1)
    print('电流限制')
    send_command(ser, 127, '90', 28696, 4)
    print('速度限制')
    send_command(ser, 127, '90', 28695, 1)
    print('角度限制')
    #π=180度
    send_command(ser, 127, '90', 28694, 10)
    time.sleep(1)
    print('角度限制')
    send_command(ser, 127, '90', 28694, 5)
    time.sleep(1)
    print('角度限制')
    send_command(ser, 127, '90', 28694, 10)
    time.sleep(1)
    print('角度限制')
    send_command(ser, 127, '90', 28694, 5)
    time.sleep(1)
    print('角度限制')
    send_command(ser, 127, '90', 28694, 0)
    time.sleep(5)
    print('重置模式')
    #ser.write(bytes.fromhex('41 54 90 07 eb fc 08 05 70 00 00 07 00 7f ff 0d 0a'))#停止
    ser.write(bytes.fromhex('41 54 20 07 eb fc 08 00 00 00 00 00 00 00 00 0d 0a'))
    # ser.close()


if __name__ == "__main__":
    main()
