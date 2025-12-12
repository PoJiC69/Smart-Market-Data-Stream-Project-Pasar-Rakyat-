import 'dart:async';
import 'dart:convert';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';

class MqttService {
  final String broker;
  final int port;
  final String clientId;
  final String topic;
  MqttServerClient? _client;

  MqttService({required this.broker, required this.port, required this.clientId, required this.topic});

  Future<bool> connect({String? username, String? password}) async {
    _client = MqttServerClient(broker, clientId);
    _client!.port = port;
    _client!.logging(on: false);
    _client!.keepAlivePeriod = 20;
    _client!.onDisconnected = onDisconnected;
    try {
      final connMess = MqttConnectMessage().withClientIdentifier(clientId).startClean();
      _client!.connectionMessage = connMess;
      final res = await _client!.connect(username, password);
      return _client!.connectionStatus!.state == MqttConnectionState.connected;
    } catch (e) {
      disconnect();
      return false;
    }
  }

  void onDisconnected() {}

  void disconnect() {
    try {
      _client?.disconnect();
    } catch (e) {}
    _client = null;
  }

  Future<bool> publish(Map<String, dynamic> payload) async {
    if (_client == null || _client!.connectionStatus!.state != MqttConnectionState.connected) {
      return false;
    }
    final builder = MqttClientPayloadBuilder();
    builder.addString(jsonEncode(payload));
    _client!.publishMessage(topic, MqttQos.atLeastOnce, builder.payload!);
    return true;
  }
}