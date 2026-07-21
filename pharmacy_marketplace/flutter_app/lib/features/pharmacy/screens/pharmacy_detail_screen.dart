import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Pharmacy detail screen — storefront view, medicine listings, location.
/// Fully implemented in Phase 3.
class PharmacyDetailScreen extends ConsumerWidget {
  const PharmacyDetailScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Pharmacy')),
      body: const Center(
        child: Text('Pharmacy Detail — Phase 3 implementation'),
      ),
    );
  }
}
