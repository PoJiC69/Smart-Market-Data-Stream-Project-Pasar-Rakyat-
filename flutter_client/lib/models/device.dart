class Device {
  final String deviceId;
  final String marketId;
  final String token;
  final String qrDataUrl;

  Device({required this.deviceId, required this.marketId, required this.token, required this.qrDataUrl});

  factory Device.fromJson(Map<String, dynamic> j) {
    return Device(
      deviceId: j['device_id'] ?? '',
      marketId: j['market_id'] ?? '',
      token: j['token'] ?? '',
      qrDataUrl: j['qr'] ?? '',
    );
  }
}