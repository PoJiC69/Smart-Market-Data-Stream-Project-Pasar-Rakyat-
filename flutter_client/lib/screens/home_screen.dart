// Modified HomeScreen to add start/stop background service buttons
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:smart_client/services/api_service.dart';
import 'package:smart_client/services/sensor_simulator.dart';
import 'package:smart_client/services/websocket_service.dart';
import 'dashboard_screen.dart';
import 'package:smart_client/services/foreground_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String status = 'idle';
  StreamSubscription? _simSub;
  bool _bgRunning = false;

  @override
  void initState() {
    super.initState();
    ForegroundService.init();
    _checkBackground();
  }

  Future<void> _checkBackground() async {
    final r = await ForegroundService.isRunning();
    setState(() => _bgRunning = r);
  }

  @override
  void dispose() {
    _simSub?.cancel();
    super.dispose();
  }

  Future<void> _startSending() async {
    final api = Provider.of<ApiService>(context, listen: false);
    final sensor = Provider.of<SensorSimulator>(context, listen: false);
    // push simulated payload every 5 seconds
    _simSub = sensor.stream(const Duration(seconds: 5)).listen((data) async {
      final payload = {
        'timestamp': data['timestamp'],
        'market_id': 'PASAR-001',
        'device_id': 'MOBILE-001',
        'temperature': data['temperature'],
        'humidity': data['humidity'],
        'crowd': data['crowd'],
        'prices': data['prices'],
      };
      final ok = await api.sendIngest(payload);
      setState(() => status = ok ? 'last sent at ${DateTime.now().toLocal()}' : 'queued/offline');
    });
    setState(() => status = 'sending');
  }

  void _stopSending() {
    _simSub?.cancel();
    setState(() => status = 'idle');
  }

  Future<void> _startBackground() async {
    final api = Provider.of<ApiService>(context, listen: false);
    final token = await api.getToken() ?? '';
    await ForegroundService.start(
      serverBase: api.baseUrl,
      token: token,
      marketId: 'PASAR-001',
      deviceId: 'MOBILE-FG-001',
      intervalMillis: 5000,
    );
    setState(() => _bgRunning = true);
  }

  Future<void> _stopBackground() async {
    await ForegroundService.stop();
    setState(() => _bgRunning = false);
  }

  @override
  Widget build(BuildContext context) {
    final api = Provider.of<ApiService>(context, listen: false);
    return Scaffold(
      appBar: AppBar(title: const Text('Smart Market Mobile Client')),
      body: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Status: $status'),
          const SizedBox(height: 12),
          ElevatedButton(onPressed: () => Navigator.pushNamed(context, '/register'), child: const Text('Register Device')),
          const SizedBox(height: 8),
          ElevatedButton(onPressed: _startSending, child: const Text('Start Simulated Sending (Foreground)')),
          const SizedBox(height: 8),
          ElevatedButton(onPressed: _stopSending, child: const Text('Stop Sending')),
          const SizedBox(height: 8),
          Row(children: [
            ElevatedButton(onPressed: _bgRunning ? null : _startBackground, child: const Text('Start Background Service')),
            const SizedBox(width: 12),
            ElevatedButton(onPressed: _bgRunning ? _stopBackground : null, child: const Text('Stop Background Service')),
          ]),
          const SizedBox(height: 16),
          ElevatedButton(
              onPressed: () {
                Navigator.of(context).push(MaterialPageRoute(builder: (_) => const DashboardScreen()));
              },
              child: const Text('Open Dashboard (Realtime)')),
        ]),
      ),
    );
  }
}