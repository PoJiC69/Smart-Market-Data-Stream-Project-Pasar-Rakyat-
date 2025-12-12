import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:smart_client/services/api_service.dart';
import 'package:smart_client/screens/home_screen.dart';
import 'package:smart_client/screens/register_screen.dart';
import 'package:smart_client/services/websocket_service.dart';
import 'package:smart_client/services/sensor_simulator.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final api = ApiService();
  final ws = WebSocketService();
  final sensorSim = SensorSimulator();
  runApp(
    MultiProvider(
      providers: [
        Provider<ApiService>(create: (_) => api),
        Provider<WebSocketService>(create: (_) => ws),
        Provider<SensorSimulator>(create: (_) => sensorSim),
      ],
      child: const SmartClientApp(),
    ),
  );
}

class SmartClientApp extends StatelessWidget {
  const SmartClientApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Market Client',
      theme: ThemeData(primarySwatch: Colors.teal),
      initialRoute: '/',
      routes: {
        '/': (context) => const HomeScreen(),
        '/register': (context) => const RegisterScreen(),
      },
    );
  }
}