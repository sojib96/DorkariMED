import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Auth state and methods — Phase 1 implementation.
/// Manages JWT tokens, phone verification status, and current user.
class AuthState {
  final bool isAuthenticated;
  final bool isPhoneVerified;
  final String? phone;
  final String? userId;

  const AuthState({
    this.isAuthenticated = false,
    this.isPhoneVerified = false,
    this.phone,
    this.userId,
  });
}

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(const AuthState());

  // Phase 1: implement login, register, verify OTP, logout
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});
