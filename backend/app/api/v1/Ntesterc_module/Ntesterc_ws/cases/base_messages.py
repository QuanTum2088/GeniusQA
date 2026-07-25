# 统一消息定义注册表
MESSAGE_REGISTRY = {
    901: {
        "name": "Login",
        "remark": "用户登录",
        "module": "protos.login_pb2",
        "req_class": "LoginReq",
        "resp_class": "LoginResp",
        "dsttype": 1,
        "resp_msg_id": 902,
        "body_template": {
            "login_token": "{{client_token}}",   # 运行时从 ctx 注入
            "client_version": "1.2.1",
            "lang": "en",
            "login_ip": "{{login_ip}}"
        }
    },
    1004: {
        "name": "CreateChargeOrder",
        "remark": "创建代收订单",
        "module": "protos.user_wallet_pb2",
        "req_class": "CreateChargeOrderReq",
        "resp_class": "CreateChargeOrderResp",
        "dsttype": 11,
        "resp_msg_id": 1005,
        "body_template": {
            "charge_id": "{{charge_id}}",        # 运行时从 ctx 提取
            "bonus_checked": False,
            "version": "1"
        }
    }
    # ...
}