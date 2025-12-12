import 'dart:async';
import 'dart:convert';
import 'package:flutter_foreground_task/flutter_foreground_task.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'sensor_simulator.dart';

/// Foreground service handler: this runs in a separate Dart isolate.
/// It must be a top-level class.
class SendTaskHandler implements TaskHandler {
  // Local simulator instance (pure Dart)
  final SensorSimulator _sim = SensorSimulator();

  // Config passed when starting the service
  late String serverBase;
  late String token;
  late String marketId;
  late String deviceId;

  @override
  Future<void> onStart(DateTime timestamp, SendPort? sendPort) async {
    // Called when the foreground task starts.
    final data = await FlutterForegroundTask.getData<String>('fg_data');
    if (data != null) {
      try {
        final Map<String, dynamic> parsed = jsonDecode(data);
        serverBase = parsed['serverBase'] ?? '';
        token = parsed['token'] ?? '';
        marketId = parsed['marketId'] ?? 'MOBILE-UNKNOWN';
        deviceId = parsed['deviceId'] ?? 'MOBILE-UNKNOWN';
      } catch (_) {
        serverBase = '';
        token = '';
        marketId = 'UNKNOWN';
        deviceId = 'UNKNOWN';
      }
    } else {
      serverBase = '';
      token = '';
      marketId = 'UNKNOWN';
      deviceId = 'UNKNOWN';
    }
  }

  @override
  Future<void> onEvent(DateTime timestamp, SendPort? sendPort) async {
    // Called on every interval tick (interval configured when starting).
    try {
      final payload = await _buildPayload();
      if (serverBase.isNotEmpty) {
        final url = Uri.parse('$serverBase/ingest');
        final headers = {'Content-Type': 'application/json'};
        if (token.isNotEmpty) headers['Authorization'] = 'Bearer $token';
        final resp = await http.post(url, headers: headers, body: jsonEncode(payload)).timeout(const Duration(seconds: 8));
        // You may inspect resp.statusCode and implement retry/queue here (not included).
      }
    } catch (e) {
      // Swallow errors to avoid crashing the background isolate; consider logging to file.
    }
  }

  Future<Map<String, dynamic>> _buildPayload() async {
    final t = _sim.nextTemperature();
    final h = _sim.nextHumidity();
    final c = _sim.nextCrowd();
    final prices = _sim.nextPrices();
    return {
      'timestamp': DateTime.now().toUtc().toIso8601String(),
      'market_id': marketId,
      'device_id': deviceId,
      'temperature': t,
      'humidity': h,
      'crowd': c,
      'prices': prices,
    };
  }

  @override
  Future<void> onDestroy(DateTime timestamp, SendPort? sendPort) async {
    // Clean up if needed when service stops.
  }
}

/// Foreground service controller utility
class ForegroundService {
  static Future<void> init() async {
    await FlutterForegroundTask.init(
      androidNotificationOptions: AndroidNotificationOptions(
        channelId: 'smart_market_channel',
        channelName: 'Smart Market Background',
        channelDescription: 'Runs background sending of sensor data',
        channelImportance: NotificationChannelImportance.LOW,
        priority: NotificationPriority.LOW,
        iconData: const NotificationIconData(
          resType: ResourceType.mipmap,
          resPrefix: ResourcePrefix.ic,
          name: 'launcher',
        ),
        // tap action will open the app
        onTapBringForeground: true,
      ),
      iosNotificationOptions: const IOSNotificationOptions(),
      foregroundTaskOptions: const ForegroundTaskOptions(
        interval: 5000, // milliseconds between onEvent calls (5 seconds)
        isOnceEvent: false,
        allowWakeLock: true,
        allowWifiLock: true,
      ),
    );
  }

  /// Start the foreground service, pass configuration via data map (serialized JSON).
  static Future<void> start({
    required String serverBase,
    required String token,
    required String marketId,
    required String deviceId,
    int intervalMillis = 5000,
  }) async {
    final init = await FlutterForegroundTask.isRunningService;
    if (init) return;

    final data = jsonEncode({
      'serverBase': serverBase,
      'token': token,
      'marketId': marketId,
      'deviceId': deviceId,
    });

    // Start foreground service with custom handler
    await FlutterForegroundTask.startService(
      notificationTitle: 'Smart Market Client',
      notificationText: 'Background sending active',
      callback: startCallback,
      foregroundTaskOptions: ForegroundTaskOptions(
        interval: intervalMillis,
        isOnceEvent: false,
        allowWakeLock: true,
        allowWifiLock: true,
      ),
    );

    // set data that will be available in TaskHandler.onStart
    await FlutterForegroundTask.setData<String>('fg_data', data);
  }

  static Future<void> stop() async {
    await FlutterForegroundTask.stopService();
  }

  static Future<bool> isRunning() => FlutterForegroundTask.isRunningService;
}

/// This must be a top-level function to be registered as callback.
void startCallback() {
  FlutterForegroundTask.setTaskHandler(SendTaskHandler());
}