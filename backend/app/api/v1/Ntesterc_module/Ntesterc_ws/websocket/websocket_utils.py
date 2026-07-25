from google.protobuf.json_format import ParseDict, MessageToDict

def proto_encode(req, body: dict) -> bytes:
    """
    将字典数据编码为Protobuf格式的二进制数据
    :param req: Protobuf消息对象(已预先定义好结构)
    :param body: 要编码的字典数据，键值对需与Protobuf消息结构匹配
    :return: bytes: 序列化后的Protobuf二进制数据
    """
    # 将字典数据解析到Protobuf消息对象中
    ParseDict(body, req)
    # 将Protobuf消息序列化为二进制数据
    return req.SerializeToString()

def proto_decode(resp, body: bytes) -> dict:
    """
    将Protobuf二进制数据解码为Python字典
    :param resp: Protobuf消息对象(已预先定义好结构，作为解析模板)
    :param body: 要解码的Protobuf二进制数据(bytes类型)
    :return dict: 包含解码后数据的字典
    """
    # 将二进制数据解析到Protobuf消息对象中
    resp.ParseFromString(body)
    # 将Protobuf消息对象转换为字典
    return MessageToDict(resp)

def encrypt_data(data: bytes) -> bytes:
    """
    使用简单的XOR算法对字节数据进行加密/解密
    功能说明:
        1. 使用固定的8字节密钥(ENCRYPT_KEY)进行循环XOR运算
        2. 加密和解密使用相同的算法(因为XOR运算的特性)
        3. 支持任意长度的输入数据
    :param data: 要加密/解密的原始字节数据(bytes对象)
    :return bytes: 加密/解密后的字节数据
    """
    # 8字节固定加密密钥(ASCII字符)
    ENCRYPT_KEY = 'EFMNJQKW'
    key_length = len(ENCRYPT_KEY)
    data_length = len(data)
    encrypted_data = bytearray(data_length)  # 预分配结果缓冲区
    key_index = 0  # 当前使用的密钥字符索引

    for i in range(data_length):
        # 获取当前密钥字符的ASCII值
        key_char = ord(ENCRYPT_KEY[key_index])
        # 执行XOR加密/解密(相同操作)
        encrypted_data[i] = data[i] ^ key_char
        # 循环使用密钥(取模运算实现密钥循环)
        key_index = (key_index + 1) % key_length

    return encrypted_data