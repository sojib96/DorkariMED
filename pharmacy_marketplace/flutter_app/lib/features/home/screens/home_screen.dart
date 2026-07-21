import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Home screen — landing page with search entry point.
/// Fully implemented in Phase 3.
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Pharmacy Marketplace')),
      body: const Center(
        child: Text('Home — Phase 3 implementation'),
      ),
    );
  }
}
