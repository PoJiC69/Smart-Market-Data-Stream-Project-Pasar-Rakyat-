import 'dart:async';
import 'dart:math';

class SensorSimulator {
  final Random _r = Random();

  double nextTemperature() => 24.0 + _r.nextDouble() * 8.0;
  double nextHumidity() => 40.0 + _r.nextDouble() * 45.0;
  int nextCrowd() => _r.nextInt(120);
  Map<String, double> nextPrices() {
    return {
      'cabai': (9000 + _r.nextDouble() * 16000).roundToDouble(),
      'bawang': (6000 + _r.nextDouble() * 10000).roundToDouble(),
      'beras': (9000 + _r.nextDouble() * 7000).roundToDouble(),
    };
  }

  Stream<Map<String, dynamic>> stream(Duration interval) async* {
    while (true) {
      await Future.delayed(interval);
      yield {
        'timestamp': DateTime.now().toUtc().toIso8601String(),
        'temperature': nextTemperature(),
        'humidity': nextHumidity(),
        'crowd': nextCrowd(),
        'prices': nextPrices(),
      };
    }
  }
}