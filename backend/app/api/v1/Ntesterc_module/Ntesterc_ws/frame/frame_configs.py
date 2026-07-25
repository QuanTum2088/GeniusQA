"""
===================================================================================
WS 私有二进制协议帧结构配置集合。
所有协议的帧结构集中定义在此文件，通过顶层 key 名称区分。FrameCodec 按名称加载对应配置，实现配置驱动的通用编解码。

配置字段说明：
byte_order : str，全局默认字节序："big"（大端）或 "little"（小端）。
fields : list[dict]，帧头字段定义列表，顺序即物理字节排列顺序。每个 field 支持以下 key：
    - name：str，字段名称
    - size：int，字节宽度
    - fixed：int | bytes，可选固定值（int 或 bytes 型魔数），未填则为动态字段
    - byte_order：str，可选，覆盖全局字节序

命名约定（FrameCodec / BaseProtocol 按约定处理，无需额外配置）
    datalen：payload 字节数，encode 时自动计算填充，decode 时用于截取 payload
    bitflag：加密标志，1=已加密；BaseProtocol.parse_message 据此决定是否解密
    cmd：命令 ID，消息路由依据；parse_message 从 header["cmd"] 取值分发
===================================================================================
"""

FRAME_CONFIGS: dict[str, dict] = {

    # ==========================================================
    # CCGame 平台私有协议 v1
    # 帧头共 32 字节固定长度，全局大端字节序
    # 物理帧布局（字节偏移 → 字段）：
    #  Offset  Size  Field    说明
    #  ------  ----  -------  ---------------------------------
    #  0       2     magic    协议魔数 FE 01，固定标识
    #  2       1     version  协议版本，当前固定 0
    #  3       1     crc      校验码，当前预留固定 0
    #  4       4     cmd      命令 ID（大端）
    #  8       2     dsttype  目标服务类型（大端）
    #  10      2     srctype  源类型，客户端固定 = 1（大端）
    #  12      4     dstid    目标实例 ID（大端）
    #  16      4     srcid    用户 UID / 源 ID（大端）
    #  20      4     seq      消息序列号（大端）
    #  24      4     bitflag  加密标志：1 = 已加密（大端）
    #  28      4     datalen  消息体字节数（大端，encode 自动填充）
    #  32+     N     payload  Protobuf 序列化后的消息体（可能已 XOR 加密）
    # ==========================================================
    "ccgame_v1": {                          # ccgame_v1，不同帧结构的配置名称，保证唯一
        "byte_order": "big",                # 全局默认字节序："big"（大端）或 "little"（小端）。
        "fields": [
            {"name": "magic", "size": 2, "fixed": b"\xFE\x01"}, # 协议魔数，固定不变，接收端可用此值校验帧合法性
            {"name": "version", "size": 1, "fixed": 0}, # 协议版本号，当前固定为 0
            {"name": "crc", "size": 1, "fixed": 0},     # CRC 校验码，当前预留未启用，固定写 0
            {"name": "cmd", "size": 4},         # 命令ID，同一业务请求和响应 ID 通常相差 1（req+1=resp）
            {"name": "dsttype", "size": 2,},    # 目标服务类型，由 PROTO_CONFIG[filename].dsttype 决定
            {"name": "srctype", "size": 2, "fixed": 1,},    # 源类型：1 = 客户端，客户端发送时固定为 1
            {"name": "dstid", "size": 4,},      # 目标实例 ID，通常为 0（由服务端内部路由）
            {"name": "srcid", "size": 4},       # 源实例 ID，即当前登录用户的 UID
            {"name": "seq", "size": 4,},        # 消息序列号，用于关联请求与响应
            {"name": "bitflag", "size": 4},     # 加密标志位：1=payload 已 XOR 加密，0=明文
            {"name": "datalen", "size": 4},     # payload 实际字节数，encode 时自动填充
        ]
    },

    # ==========================================================
    # 示例：轻量级私有协议 v1（16 字节小端序头，无魔数，无加密）
    # 适用场景：内部微服务间通信，消息体为 JSON
    #
    # 物理帧布局：
    #  Offset  Size  Field    说明
    #  ------  ----  -------  ---------------------------------
    #  0       4     cmd      命令 ID（小端）
    #  4       4     srcid    用户 UID（小端）
    #  8       4     seq      序列号（小端）
    #  12      4     datalen  payload 字节数（小端，encode 自动填充）
    #  16+     N     payload  JSON 序列化的消息体（明文）
    # ==========================================================
    "simple_v1": {
        "byte_order": "little",
        "fields": [
            {"name": "cmd",     "size": 4},
            {"name": "srcid",   "size": 4},
            {"name": "seq",     "size": 4},
            {"name": "datalen", "size": 4},
        ],
    },
}
