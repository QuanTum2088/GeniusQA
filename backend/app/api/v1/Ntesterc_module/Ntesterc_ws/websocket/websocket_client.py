"""
WsClient: WebSocket 连接客户端，负责连接管理与通用消息收发。

--------职责--------
- WebSocket 连接的建立、维持、关闭（on_open / on_close / on_error）
- 定时心跳线程（_ping_loop）
- 消息接收分发：将收到的消息按 msg_id 放入对应响应队列
- 通用发送接口：send() / send_and_wait()
- 业务钩子：on_connected() / on_received()，子类覆盖实现具体业务逻辑

------与 BaseProtocol 的分工------
WsClient     协议无关，只负责网络 I/O 和线程管理
BaseProtocol 负责所有协议处理（帧编解码、序列化、加密、路由、断言）

--------使用方式--------
  # 直接使用
  client = WsClient(url, protocol=BaseProtocol(), uid=12345)
  client.run()

  # 继承使用（添加业务逻辑）
  class PaymentWsClient(WsClient):
      def on_connected(self, ws):
          self.send(901, self.req_msg[901])       # 连接后自动登录

      def on_received(self, msg_id, msg):
          if msg_id == 902:
              self.uid = msg.get("userId", self.uid)
"""

from __future__ import annotations
import queue
import threading

import websocket
from loguru import logger
from app.api.v1.Ntesterc_module.Ntesterc_ws.protocol.base_protocol import BaseProtocol


class WebsocketClient:
    """
    WebSocket 连接客户端。

    核心机制：响应队列
    -----------------
    send_and_wait() 调用时：
      1. 提前注册 _response_queues[resp_msg_id] = Queue()（必须在 send 前，防竞态）
      2. 发送请求消息
      3. 阻塞等待队列，_on_message 收到对应 msg_id 时放入数据
      4. 返回响应或超时返回 None，finally 中清理注册

    线程安全
    --------
    _response_queues 读写通过 self._lock 加锁，_on_message 和 send_and_wait
    运行在不同线程，保证并发安全。
    """

    def __init__(self, url: str, protocol: BaseProtocol, uid: int = 0):
        """
        :param url:      WebSocket 服务端地址
        :param protocol: 协议处理实例，负责帧编解码、序列化、加密、路由
        :param uid:      当前用户 UID，写入帧头 srcid；登录后业务层更新
        """
        self.protocol = protocol
        self.uid      = uid

        self._response_queues: dict[int, queue.Queue] = {}
        self._lock        = threading.Lock()
        self._stop_ping   = threading.Event()
        self._ping_thread = None

        self._ws = websocket.WebSocketApp(
            url,
            on_open    = self._on_open,
            on_message = self._on_message,
            on_error   = self._on_error,
            on_close   = self._on_close,
            on_ping    = self._on_ping,
            on_pong    = self._on_pong,
        )

    # ==================================================================
    # 公共接口
    # ==================================================================

    def send(self, msg_id: int, data: dict, seq: int = 0) -> None:
        """
        发送一条 WS 消息（不等待响应）。

        :param msg_id: 命令 ID
        :param data:   消息体业务字段 dict
        :param seq:    消息序列号，默认 0
        """
        frame = self.protocol.build_message(msg_id, data, self.uid, seq)
        self._ws.send(frame)
        logger.info(f"send_msg({msg_id}): {data}")

    def send_and_wait(self, msg_id: int, data: dict,
                      timeout: int = 20) -> dict | None:
        """
        发送消息并阻塞等待对应响应，超时返回 None。

        :param msg_id:  请求命令 ID
        :param data:    消息体业务字段 dict
        :param timeout: 最长等待秒数，默认 20s
        :return:        响应消息体 dict，超时返回 None

        关键步骤
        --------
        1. get_resp_msg_id() 获取期望响应 msg_id（默认 req+1）
        2. send 前注册队列（避免响应先于等待到达而丢失）
        3. send() 发送请求
        4. q.get(timeout) 阻塞等待
        5. finally 清理队列，不泄漏内存
        """
        resp_id = self.protocol.get_resp_msg_id(msg_id)
        q = queue.Queue()
        with self._lock:
            self._response_queues[resp_id] = q
        try:
            self.send(msg_id, data)
            return q.get(timeout=timeout)
        except queue.Empty:
            logger.warning(f"等待响应超时 resp_msg_id={resp_id}（{timeout}s）")
            return None
        finally:
            with self._lock:
                self._response_queues.pop(resp_id, None)

    def run(self) -> None:
        """启动 WebSocket 连接（阻塞运行直到连接关闭）。"""
        self._ws.run_forever()

    def close(self) -> None:
        """优雅关闭：先停止心跳线程，再关闭 WebSocket 连接。"""
        self._stop_ping_thread()
        if self._ws:
            self._ws.close()

    # ==================================================================
    # 业务钩子（子类覆盖）
    # ==================================================================

    def on_connected(self, ws) -> None:
        """
        WS 连接建立后的业务入口钩子，默认空实现。

        :param ws: WebSocketApp 实例

        子类覆盖此方法实现连接后逻辑（如自动登录）。
        在独立线程中调用，不阻塞 WebSocketApp 事件循环。
        """
        pass

    def on_received(self, msg_id: int, msg: dict) -> None:
        """
        每条非忽略消息到达时触发，默认空实现。

        :param msg_id: 收到消息的命令 ID
        :param msg:    反序列化后的消息体 dict

        子类覆盖处理服务端主动推送（无对应 send_and_wait 等待的消息）。
        """
        pass

    # ==================================================================
    # WebSocket 生命周期回调（内部）
    # ==================================================================

    def _on_open(self, ws):
        """连接建立：清除停止标志、启动心跳线程、独立线程调用 on_connected()。"""
        logger.info("WebSocket 连接已建立")
        self._stop_ping.clear()
        self._ping_thread = threading.Thread(
            target=self._ping_loop, args=(ws,), daemon=True
        )
        self._ping_thread.start()
        threading.Thread(target=self.on_connected, args=(ws,), daemon=True).start()

    def _on_message(self, ws, raw: bytes):
        """
        收到消息：解析 -> 过滤忽略 -> 放入响应队列 -> 触发业务钩子。

        :param raw: 原始二进制数据
        """
        try:
            msg_id, msg = self.protocol.parse_message(raw)
        except Exception as e:
            logger.error(f"消息解析失败: {e}")
            return

        if self.protocol.is_ignored(msg_id):
            return

        logger.info(f"received_msg({msg_id}): {msg}")

        with self._lock:
            if msg_id in self._response_queues:
                self._response_queues[msg_id].put(msg)

        self.on_received(msg_id, msg)

    def _on_error(self, ws, error):
        logger.error(f"WebSocket Error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        logger.info(f"WebSocket Closed: code={close_status_code}, msg={close_msg}")
        self._stop_ping_thread()

    def _on_ping(self, ws, message):
        """收到 PING 帧，发送协议级心跳（opcode=0x9）。"""
        data  = self.protocol.heartbeat_data()
        frame = self.protocol.build_message(
            self.protocol.HEARTBEAT_MSG_ID, data, self.uid
        )
        ws.send(frame, opcode=0x9)

    def _on_pong(self, ws, raw: bytes):
        """收到 PONG 帧，尝试解析内容用于调试，失败静默处理。"""
        if not raw:
            return
        try:
            msg_id, msg = self.protocol.parse_message(raw)
            logger.debug(f"pong({msg_id}): {msg}")
        except Exception:
            pass

    # ==================================================================
    # 心跳管理（内部）
    # ==================================================================

    def _ping_loop(self, ws):
        """
        心跳线程主循环，按 HEARTBEAT_INTERVAL 定期发送协议级心跳帧。

        :param ws: WebSocketApp 实例

        使用 Event.wait(interval) 替代 time.sleep()，停止信号可即时响应。
        ws.sock 为 None 或发送失败时主动退出循环。
        """
        try:
            while not self._stop_ping.wait(self.protocol.HEARTBEAT_INTERVAL):
                if not ws.sock:
                    logger.warning("连接已断开，心跳线程退出")
                    break
                try:
                    data  = self.protocol.heartbeat_data()
                    frame = self.protocol.build_message(
                        self.protocol.HEARTBEAT_MSG_ID, data, self.uid
                    )
                    ws.send(frame, opcode=0x9)
                except Exception as e:
                    logger.error(f"心跳发送失败: {e}")
                    break
        finally:
            logger.info("心跳线程已停止")

    def _stop_ping_thread(self):
        """通知心跳线程停止，等待退出（最多 2 秒）。"""
        self._stop_ping.set()
        if self._ping_thread and self._ping_thread.is_alive():
            self._ping_thread.join(timeout=2)
