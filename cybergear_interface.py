import logging
import serial
import time
import os
import struct

result = os.popen("sudo ls -l /dev/ttyCH341*").read()
# sudo chmod 666 /dev/ttyACM* 有时会报错，显示无曲线打开串口，这时需运行左侧命令
com = result.split()[-1]
os.system("sudo chmod 777 " + com)
os.system("sudo fuser -k " + com)
ser = serial.Serial(com, 921600, timeout=1)

print(f"进入<AT命令模式>")
ser.write(bytes.fromhex('41 54 2b 41 54 0d 0a'))

#参数转通信
def float_to_bytes(f):
    """将浮点数转换为带空格的字节表示字符串"""
    byte_val = struct.pack('<f', f)
    return ' '.join('{:02x}'.format(b) for b in byte_val)

#通信转参数


def bytes_to_float(byte_str):
    """将带空格的字节表示字符串转换为浮点数"""
    bytes_without_space = bytes.fromhex(byte_str.replace(' ', ''))
    return struct.unpack('<f', bytes_without_space)[0]

#通信转CANID


def bytes_to_value(value):
    # Convert integer to hex string
    hex_str = "{:04x}".format(value)
    # Extract the high byte from the hex string
    high_byte = int(hex_str[:2], 16)
    # Return the calculated value
    return 123 + (high_byte - 0xDC) // 8


#CANID转通信
def value_to_bytes(value):
    # 根据规律计算高位字节
    high_byte = 0xDC + (value - 123) * 8
    # 返回字节字符串
    return '{:02x} 08'.format(high_byte)


def parse_command(command_str):
    return [int(x, 16) for x in command_str.split()]


def reverse_bytes(hex_str):
    # 去除前缀"0X"或"0x"
    hex_str = hex_str[2:] if hex_str.startswith(('0X', '0x')) else hex_str
    # 确保输入长度为偶数，为每个字节提供两个字符
    if len(hex_str) % 2 != 0:
        hex_str = '0' + hex_str

    # 使用列表推导反转字节顺序，并使用join方法将其组合成字符串
    reversed_str = ' '.join([hex_str[i:i+2]
                            for i in range(0, len(hex_str), 2)][::-1])
    return reversed_str


def send_command(can_id, cmd_mode, index, value):
    id_num = value_to_bytes(can_id)
    index_num = reverse_bytes(hex(index))
    value_num = float_to_bytes(value)
    date = f"41 54 {cmd_mode} 07 eb {id_num} {index_num} 00 00 {value_num} 0d 0a"
    try:
        # 将电机向前旋转1秒
        ser.write(bytes.fromhex(date))
        response = ser.readline()
        hex_string = ' '.join([response[i:i+1].hex()
                               for i in range(len(response))])
        print(f"RX: {hex_string}")
        time.sleep(1)

    except Exception as e:
        print(f"An error occurred: {e}")
    return hex_string


print('这个不知道啥意思，有使能的作用')
ser.write(bytes.fromhex('41 54 90 07 eb fc 08 05 70 00 00 01 00 00 00 0d 0a'))
response = ser.readline()
print(f"RX: {response}")
time.sleep(5)
print('模式1位置模式')
send_command(127, '18', 0X7005, 1)
print('电流限制')
send_command(127, '90', 0X7018, 4)
print('速度限制')
send_command(127, '90', 0X7017, 1)
print('角度限制')
send_command(127, '90', 0X7016, 10)
time.sleep(1)
print('角度限制')
send_command(127, '90', 0X7016, 5)
time.sleep(1)
print('角度限制')
send_command(127, '90', 0X7016, 10)
time.sleep(1)
print('角度限制')
send_command(127, '90', 0X7016, 5)
time.sleep(1)
print('角度限制')
send_command(127, '90', 0X7016, 10)
time.sleep(5)
print('停止')
ser.write(bytes.fromhex('41 54 90 07 eb fc 08 05 70 00 00 07 00 7f ff 0d 0a'))
#ser.close()
