import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import 'package:flutter/material.dart';

typedef OnPriceUpdate = void Function(List<dynamic> data);

class WebSocketService {
  WebSocketChannel? _channel;
  StreamSubscription? _sub;

  void connect(String uri, {OnPriceUpdate? onUpdate}) {
    disconnect();
    try {
      _channel = WebSocketChannel.connect(Uri.parse(uri));
      _sub = _channel!.stream.listen((msg) {
        try {
          final obj = jsonDecode(msg);
          if (obj is Map && obj['type'] == 'price_update') {
            if (onUpdate != null) onUpdate(List.from(obj['data'] ?? []));
          }
        } catch (e) {
          debugPrint('WS parse err: $e');
        }
      }, onDone: () {
        debugPrint('WS done');
      }, onError: (e) {
        debugPrint('WS error: $e');
      });
    } catch (e) {
      debugPrint('WS connect failed: $e');
    }
  }

  void disconnect() {
    try {
      _sub?.cancel();
      _channel?.sink.close(status.goingAway);
    } catch (_) {}
    _channel = null;
    _sub = null;
  }

  void send(Map<String, dynamic> payload) {
    try {
      _channel?.sink.add(jsonEncode(payload));
    } catch (e) {}
  }
}