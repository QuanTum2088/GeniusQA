from __future__ import annotations
import importlib
import time

from google.protobuf.json_format import ParseDict, MessageToDict
from app.api.v1.Ntesterc_module.Ntesterc_ws.frame.frame_codec import FrameCodec


"""
======================================================================
BaseProtocol: WS 私有二进制协议基类。

--------------职责--------------
封装与协议本身直接相关的所有处理逻辑:
  - 消息体序列化/反序列化（默认 Protobuf）
  - 消息体加密/解密（默认 XOR）
  - 消息路由（msg_id -> proto 类 + dsttype）
  - 发送链路骨架: build_message()
  - 接收链路骨架: parse_message()
  - 响应断言: assert_response()

-------与 FrameCodec 的分工------
  FrameCodec   负责帧的物理编解码（字段打包/解包），不感知协议语义
  BaseProtocol 负责协议语义（序列化/加密/路由），内部持有 FrameCodec 实例

----------扩展使用方式----------
  1. 仅帧头不同    -> 子类覆盖 FRAME_NAME 指向 FRAME_CONFIGS 中的另一条配置
  2. 序列化不同    -> 子类覆盖 serialize() / deserialize()
  3. 加密不同      -> 子类覆盖 encrypt() / decrypt()
  4. 路由不同      -> 子类覆盖 get_msg_meta() / get_resp_msg_id()
  5. 断言不同      -> 子类覆盖 assert_response()
  6. 帧结构极特殊  -> 子类替换 self.codec = MyExoticCodec(...)
======================================================================
"""
class BaseProtocol:
    """
    WS 私有二进制协议基类，默认实现对应 CCGame v1 协议
    （32 字节大端帧头 + Protobuf 序列化 + XOR 加密）。

    类变量（子类直接覆盖即可，无需改动方法）
    ----------------------------------------
    FRAME_NAME         对应 frame_configs.py 中 FRAME_CONFIGS 的协议名称
    ENCRYPT_KEY        XOR 加密密钥（bytes 类型）
    HEARTBEAT_MSG_ID   心跳命令 ID
    HEARTBEAT_INTERVAL 心跳间隔（秒）
    IGNORED_MSG_IDS    收到后不做处理的消息 ID 集合

    命名约定（与 frame_configs.py 字段命名对应）
    ------------------------------------
    CMD_FIELD      header dict 中命令 ID 的 key，默认 "cmd"
    ENCRYPT_FIELD  header dict 中加密标志的 key，默认 "bitflag"
    """

    FRAME_NAME         = "ccgame_v1"
    ENCRYPT_KEY        = b"EFMNJQKW"   # XOR 固定密钥（8 字节，循环使用）
    HEARTBEAT_MSG_ID   = 1600
    HEARTBEAT_INTERVAL = 8
    IGNORED_MSG_IDS    = {1600, 3403}

    CMD_FIELD     = "cmd"
    ENCRYPT_FIELD = "bitflag"

    def __init__(self):
        self.codec = FrameCodec.from_name(self.FRAME_NAME)

    # ==================================================================
    #        发送链路骨架（子类通常不覆盖）
    # ==================================================================
    def build_message(self, msg_id: int, data: dict,
                      uid: int, seq: int = 0) -> bytes:
        """
        发送链路骨架：将业务数据构造为可直接发送的完整二进制帧。

        :param msg_id: 命令 ID，如 901（登录）、1004（代收下单）
        :param data:   消息体字段 dict，与 proto 消息结构对应
        :param uid:    当前用户 UID，写入帧头 srcid 字段
        :param seq:    消息序列号，默认 0
        :return:       完整二进制帧 bytes

        流程: get_msg_meta -> serialize -> encrypt -> codec.encode
        """
        #（1）根据命令 ID 获取对应的 proto 类实例和目标服务类型（dsttype）。
        _, dsttype = self.get_msg_meta(msg_id)
        #（2）将业务 dict 序列化为消息体字节流。默认：Protobuf。
        raw        = self.serialize(msg_id, data)
        #（3）加密消息体。默认：XOR 循环密钥加密。
        encrypted  = self.encrypt(raw)
        #（4）将消息体 payload 和动态字段值打包为完整二进制帧（帧头 + payload）。
        return self.codec.encode(
            encrypted, cmd=msg_id, dsttype=dsttype, srcid=uid, seq=seq, bitflag=1, dstid=0)


    # ==================================================================
    #        接收链路骨架（子类通常不覆盖）
    # ==================================================================
    def parse_message(self, raw: bytes) -> tuple[int, dict]:
        """
        接收链路骨架：将收到的原始二进制帧解析为 (msg_id, 消息体 dict)。
        :param raw: WebSocket on_message 收到的原始二进制数据
        :return:    (msg_id, msg)
        流程: codec.decode -> decrypt（按 bitflag 决定）-> deserialize
        """
        #（1）将原始二进制帧解析为帧头字段 dict 和 payload bytes
        header, payload = self.codec.decode(raw)
        #（2）解密消息体。默认：与 encrypt 相同（XOR 对称算法）
        if header.get(self.ENCRYPT_FIELD, 0) == 1:
            payload = self.decrypt(payload)
        msg_id = header[self.CMD_FIELD]
        #（3）将消息体字节流反序列化为业务 dict。
        return msg_id, self.deserialize(msg_id, payload)

    # ==================================================================
    #           可覆盖方法（子类按需覆盖）
    # ==================================================================
    def serialize(self, msg_id: int, data: dict) -> bytes:
        """
        将业务 dict 序列化为消息体字节流。默认：Protobuf。
        :param msg_id: 命令 ID，用于获取对应的 proto 类
        :param data:   业务字段 dict，key 需与 proto 字段定义一致
        :return:       SerializeToString() 后的字节流
        子类覆盖场景：消息体使用 JSON / MessagePack / 自定义二进制格式
        """
        proto, _ = self.get_msg_meta(msg_id)
        ParseDict(data, proto)
        return proto.SerializeToString()

    def deserialize(self, msg_id: int, raw: bytes) -> dict:
        """
        将消息体字节流反序列化为业务 dict。默认：Protobuf。
        :param msg_id: 命令 ID，用于获取对应的 proto 类（作为解析模板）
        :param raw:    已解密的消息体字节流
        :return:       MessageToDict() 转换后的业务字段 dict
        子类覆盖场景：消息体使用 JSON / MessagePack / 自定义二进制格式
        """
        proto, _ = self.get_msg_meta(msg_id)
        proto.ParseFromString(raw)
        return MessageToDict(proto)

    def encrypt(self, data: bytes) -> bytes:
        """
        加密消息体。默认：XOR 循环密钥加密。
        :param data: 待加密的原始字节流
        :return:     加密后的字节流
        XOR 原理：使用 8 字节密钥与数据逐字节异或，密钥不足时循环复用。
        XOR 具有对称性，encrypt == decrypt，两次操作还原原始数据。
        子类覆盖场景：使用 AES / RSA / 自定义加密算法
        """
        key  = self.ENCRYPT_KEY
        klen = len(key)
        return bytes(b ^ key[i % klen] for i, b in enumerate(data))

    def decrypt(self, data: bytes) -> bytes:
        """
        解密消息体。默认：与 encrypt 相同（XOR 对称算法）。
        :param data: 待解密的加密字节流
        :return:     解密后的原始字节流
        子类覆盖场景：AES 等非对称加密需分别实现 encrypt / decrypt
        """
        return self.encrypt(data)

    def get_msg_meta(self, msg_id: int) -> tuple:
        """
        根据命令 ID 获取对应的 proto 类实例和目标服务类型（dsttype）。
        :param msg_id: 命令 ID，如 901、1002、1004
        :return: (proto_class_instance, dsttype)
               proto_class_instance -- 已实例化的 proto 类，序列化/反序列化用
               dsttype             -- 目标服务类型，写入帧头 dsttype 字段
        子类覆盖场景：使用自定义消息映射表或其他序列化框架
        """
        import jsonpath

        # 默认实现：从 PROTO_CONFIG 查找 msg_id 对应的 proto 文件名和类名，
        filename, classname = find_key_and_message_by_value(PROTO_CONFIG, msg_id)
        dsttype = jsonpath.jsonpath(PROTO_CONFIG, f"$.{filename}.dsttype")[0]

        # 通过 importlib 动态导入并实现实例化
        mod = importlib.import_module(f"protos.{filename}")
        return getattr(mod, classname)(), dsttype

    def get_resp_msg_id(self, req_msg_id: int) -> int:
        """
        获取请求对应的响应命令 ID。默认：req_msg_id + 1。

        :param req_msg_id: 请求命令 ID
        :return:           期望收到的响应命令 ID

        CCGame 协议规律：响应 ID = 请求 ID + 1。
        例：登录 901 -> 响应 902，代收 1004 -> 响应 1005。

        子类覆盖场景：响应 ID 与请求 ID 无固定规律，需使用显式映射表
        """
        return req_msg_id + 1

    def assert_response(self, msg_id: int, resp: dict) -> tuple[bool, str]:
        """
        对收到的响应执行业务断言。

        :param msg_id: 响应命令 ID
        :param resp:   反序列化后的响应消息体 dict
        :return:       (passed, reason)，passed=False 时 reason 说明原因

        默认实现：不做任何断言，直接返回通过。
        子类覆盖场景：检查 ret 错误码、验证必要字段等。
        覆盖示例:
            if msg_id == 1005:
                ret = resp.get("ret")
                if ret == 1:   return False, "代收金额不匹配或通道维护"
                if ret == -15: return False, "环境配置错误"
                if ret:        return False, f"未知错误 ret={ret}"
            return True, ""
        """
        return True, ""

    def is_ignored(self, msg_id: int) -> bool:
        """
        判断该 msg_id 的消息是否忽略（不入响应队列、不记录业务日志）。

        :param msg_id: 收到消息的命令 ID
        :return:       True=忽略

        默认忽略：心跳响应（1600）和特定服务端推送（3403）
        """
        return msg_id in self.IGNORED_MSG_IDS

    def heartbeat_data(self) -> dict:
        """
        构造心跳消息体 dict。

        :return: 默认使用毫秒时间戳作为 trans 字段

        子类覆盖场景：心跳消息体结构与默认不同
        """
        return {"trans": str(int(time.time() * 1000))}
