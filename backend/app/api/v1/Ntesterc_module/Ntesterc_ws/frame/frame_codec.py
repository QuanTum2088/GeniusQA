from .frame_configs import FRAME_CONFIGS

"""
FrameCodec：配置驱动的通用二进制帧编解码器。
--------设计思路--------
不同私有二进制协议的帧头差异，本质上是字段排列顺序、字节宽度、字节序、固定值（魔数/保留字段）不同。
将这些差异描述为配置（frame_configs.py），FrameCodec 按配置通用处理，做到"改配置即换协议"。

--------扩展方式--------
- 常见协议差异（字段顺序/宽度/字节序）→ 在 frame_configs.py 新增配置，零代码改动
- 极特殊结构（TLV、变长头、校验码计算）→ 继承 FrameCodec，覆盖 encode/decode
"""

class FrameCodec:

    #  配置中名为 "datalen" 的字段为 payload 长度字段：
    #   - encode 时自动计算 len(payload) 并填入，调用方无需传入
    #   - decode 时读取该值以截取正确长度的 payload
    DATALEN_FIELD = "datalen"

    def __init__(self, config: dict):
        """
        :param config: 单个协议的帧结构配置 dict（FRAME_CONFIGS 中的一条）
        """
        self.fields     = config["fields"]
        self.default_bo = config.get("byte_order", "big")

    def encode(self, payload: bytes, **field_values) -> bytes:
        """
        将消息体 payload 和动态字段值打包为完整二进制帧（帧头 + payload）。
        :param payload: 已序列化（及加密）的消息体字节
        :param field_values: JSON格式动态字段值，key=字段名，value=int
                例：cmd=901, dsttype=11, srcid=89901928, bitflag=1；固定字段（fixed）和 datalen 无需传入
        :return: 完整二进制帧 bytes
        """
        # 1. 设置 自动计算的 datalen（约定的 payload 长度字段名） 长度值
        field_values[self.DATALEN_FIELD] = len(payload)   # 步骤 1
        parts: list[bytes] = []

        # 2. 遍历字段列表，按顺序决定每个字段的值：
        for f in self.fields:
            # 按顺序获取字节宽度（size）和默认字节序（byte_order）
            size = f["size"]
            bo   = f.get("byte_order", self.default_bo)
            # 判断有默认值使用配置值（魔数、保留字节等），无默认值获取配置name名称
            val = f["fixed"] if "fixed" in f else field_values.get(f["name"], 0)

            # 3. 将字段值按字节序转换为 bytes：
            if isinstance(val, (bytes, bytearray)):
                # bytes/bytearray 型（魔数）→ 直接截取指定长度
                parts.append(bytes(val)[:size])
            else:   #  int 型 → to_bytes(size, byte_order) 打包
                parts.append(int(val).to_bytes(size, bo))

        # 4. 拼接所有字段字节 + payload 返回
        return b"".join(parts) + payload


    def decode(self, data: bytes) -> tuple[dict, bytes]:
        """
        将原始二进制帧解析为帧头字段 dict 和 payload bytes。
        :param data: WebSocket on_message 收到的原始二进制数据
        :return: (header, payload)
                 header  — dict，key=字段名，value=int 或 bytes（魔数类字段）
                 payload — 消息体原始字节，可能仍为加密状态，由上层决定是否解密
        """
        # 1. offset=0，从头按字段顺序读取
        header: dict = {}
        offset = 0

        # 2. 每次读取 data[offset:offset+size]：
        for f in self.fields:
            size  = f["size"]
            raw   = data[offset: offset + size]
            offset += size                  # offset 累加字段宽度
            bo    = f.get("byte_order", self.default_bo)
            fixed = f.get("fixed")

            # fixed 值为 bytes 型（魔数）→ 原样保存为 bytes
            if isinstance(fixed, (bytes, bytearray)):
                header[f["name"]] = bytes(raw)
            else:   # 其他字段 → 按字节序转换为 int
                header[f["name"]] = int.from_bytes(raw, bo)

        # 步骤 3：截取 payload；若无 datalen 字段则取剩余全部字节
        datalen = header.get(self.DATALEN_FIELD, len(data) - offset)
        payload = data[offset: offset + datalen]
        return header, payload


    @classmethod
    def from_name(cls, name: str) -> "FrameCodec":
        """
        按协议名称从 FRAME_CONFIGS 创建 FrameCodec 实例。

        :param name: FRAME_CONFIGS 中的协议名称，如 "ccgame_v1"
        :return:     对应配置的 FrameCodec 实例
        :raises KeyError: 名称不存在时抛出，并提示可用名称列表
        """
        if name not in FRAME_CONFIGS:
            raise KeyError(
                f"帧结构配置 '{name}' 不存在，"
                f"可用配置：{list(FRAME_CONFIGS.keys())}"
            )
        return cls(FRAME_CONFIGS[name])
