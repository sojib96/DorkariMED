import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Pharmacy state and methods — Phase 3 implementation.
class PharmacyState {
  final List<dynamic> pharmacies;
  final bool isLoading;

  const PharmacyState({
    this.pharmacies = const [],
    this.isLoading = false,
  });
}

class PharmacyNotifier extends StateNotifier<PharmacyState> {
  PharmacyNotifier() : super(const PharmacyState());

  // Phase 3: implement nearby search, detail fetch
}

final pharmacyProvider =
    StateNotifierProvider<PharmacyNotifier, PharmacyState>((ref) {
  return PharmacyNotifier();
});
