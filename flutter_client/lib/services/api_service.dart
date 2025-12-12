import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:smart_client/models/device.dart';

class ApiService {
  // Update base url if needed
  String baseUrl = 'http://10.0.2.2:8000'; // Android emulator -> host machine; use localhost for iOS simulator
  final _storage = const FlutterSecureStorage();

  Future<Map<String, dynamic>> registerDevice({required String marketId, required String deviceId, String role = 'operator'}) async {
    final url = Uri.parse('$baseUrl/api/auth/device/register');
    final resp = await http.post(url, headers: {'Content-Type': 'application/json'}, body: jsonEncode({'market_id': marketId, 'device_id': deviceId, 'role': role}));
    if (resp.statusCode >= 200 && resp.statusCode < 300) {
      final data = jsonDecode(resp.body) as Map<String, dynamic>;
      final token = data['token'] as String?;
      if (token != null) {
        await saveToken(token);
      }
      return data;
    } else {
      return {'error': 'status ${resp.statusCode}', 'body': resp.body};
    }
  }

  Future<void> saveToken(String token) async {
    await _storage.write(key: 'device_token', value: token);
  }

  Future<String?> getToken() async {
    return await _storage.read(key: 'device_token');
  }

  Future<bool> sendIngest(Map<String, dynamic> payload) async {
    final url = Uri.parse('$baseUrl/ingest');
    final token = await getToken();
    final headers = {'Content-Type': 'application/json'};
    if (token != null) headers['Authorization'] = 'Bearer $token';
    final resp = await http.post(url, headers: headers, body: jsonEncode(payload));
    return resp.statusCode >= 200 && resp.statusCode < 300;
  }

  Future<Map<String, dynamic>> validatePrice(String marketId, String commodity, double price) async {
    final url = Uri.parse('$baseUrl/api/validation/price/check');
    final resp = await http.post(url, headers: {'Content-Type': 'application/json'}, body: jsonEncode({'market_id': marketId, 'commodity': commodity, 'price': price}));
    return jsonDecode(resp.body);
  }
}