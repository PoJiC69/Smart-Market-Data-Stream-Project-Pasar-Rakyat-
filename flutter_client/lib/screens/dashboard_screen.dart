import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'dart:math';
import 'package:smart_client/services/websocket_service.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final List<FlSpot> _spots = [];
  final List<Color> _dotColors = [];
  int _xIdx = 0;
  WebSocketService? _ws;

  @override
  void initState() {
    super.initState();
    _ws = Provider.of<WebSocketService>(context, listen: false);
    // update this URL to your platform websocket endpoint
    final wsUri = 'ws://10.0.2.2:8000/ws/prices?market_id=PASAR-001&commodity=cabai';
    _ws!.connect(wsUri, onUpdate: _onPriceUpdate);
  }

  @override
  void dispose() {
    _ws?.disconnect();
    super.dispose();
  }

  void _onPriceUpdate(List<dynamic> data) {
    // data: list of items including price, impact_score, timestamp
    for (final dp in data) {
      final price = (dp['price'] ?? dp['y'] ?? 0).toDouble();
      final impact = (dp['impact_score'] ?? 0).toDouble();
      setState(() {
        _spots.add(FlSpot(_xIdx.toDouble(), price));
        _dotColors.add(_impactColor(impact));
        if (_spots.length > 50) {
          _spots.removeAt(0);
          _dotColors.removeAt(0);
          for (int i = 0; i < _spots.length; i++) {
            _spots[i] = FlSpot(i.toDouble(), _spots[i].y);
          }
          _xIdx = _spots.length;
        } else {
          _xIdx++;
        }
      });
    }
  }

  Color _impactColor(double score) {
    if (score <= 20) return Colors.green;
    if (score <= 50) return Colors.orange;
    if (score <= 80) return Colors.deepOrange;
    return Colors.red;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Realtime Dashboard')),
      body: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(children: [
          Expanded(
            child: LineChart(
              LineChartData(
                minY: 0,
                lineBarsData: [
                  LineChartBarData(spots: _spots, isCurved: true, dotData: FlDotData(getDotPainter: (spot, percent, bar, index) {
                    final color = _dotColors[index % _dotColors.length];
                    return FlDotCirclePainter(radius: 4, color: color, strokeWidth: 0);
                  })),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          ElevatedButton(onPressed: () {}, child: const Text('Refresh / no-op')),
        ]),
      ),
    );
  }
}