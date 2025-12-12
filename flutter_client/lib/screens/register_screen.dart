import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:smart_client/services/api_service.dart';
import 'package:qr_code_scanner/qr_code_scanner.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _deviceCtrl = TextEditingController();
  final _marketCtrl = TextEditingController();
  bool _loading = false;
  String _qrDataUrl = '';

  @override
  void dispose() {
    _deviceCtrl.dispose();
    _marketCtrl.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    final api = Provider.of<ApiService>(context, listen: false);
    setState(() => _loading = true);
    final res = await api.registerDevice(marketId: _marketCtrl.text.trim(), deviceId: _deviceCtrl.text.trim());
    setState(() => _loading = false);
    if (res.containsKey('error')) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Register failed: ${res['error']}')));
    } else {
      setState(() {
        _qrDataUrl = res['qr'] ?? '';
      });
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Registered successfully')));
    }
  }

  void _openScanner() async {
    final result = await Navigator.push(context, MaterialPageRoute(builder: (_) => const QRScannerPage()));
    if (result != null && result is String) {
      // Platform returned raw QR payload string — platform's register returned a dict payload string.
      // For convenience, try to parse expected token or display it.
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Scanned: $result')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(title: const Text('Register Device')),
        body: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(children: [
            TextField(controller: _marketCtrl, decoration: const InputDecoration(labelText: 'Market ID', hintText: 'PASAR-001')),
            TextField(controller: _deviceCtrl, decoration: const InputDecoration(labelText: 'Device ID', hintText: 'DEV-001')),
            const SizedBox(height: 12),
            ElevatedButton(onPressed: _loading ? null : _register, child: _loading ? const CircularProgressIndicator() : const Text('Register')),
            const SizedBox(height: 12),
            ElevatedButton(onPressed: _openScanner, child: const Text('Scan QR')),
            if (_qrDataUrl.isNotEmpty) ...[
              const SizedBox(height: 12),
              const Text('QR (platform returned):'),
              Image.memory(Uri.parse(_qrDataUrl).data!.contentAsBytes()),
            ],
          ]),
        ));
  }
}

class QRScannerPage extends StatefulWidget {
  const QRScannerPage({super.key});
  @override
  State<QRScannerPage> createState() => _QRScannerPageState();
}

class _QRScannerPageState extends State<QRScannerPage> {
  final GlobalKey qrKey = GlobalKey(debugLabel: 'QR');
  Barcode? result;
  QRViewController? controller;

  @override
  void dispose() {
    controller?.dispose();
    super.dispose();
  }

  void _onQRViewCreated(QRViewController ctrl) {
    controller = ctrl;
    ctrl.scannedDataStream.listen((scanData) {
      controller?.pauseCamera();
      Navigator.of(context).pop(scanData.code);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: const Text('Scan QR')), body: QRView(key: qrKey, onQRViewCreated: _onQRViewCreated));
  }
}