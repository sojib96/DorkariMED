import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pharmacy_marketplace/features/auth/screens/login_screen.dart';
import 'package:pharmacy_marketplace/features/auth/screens/register_screen.dart';

void main() {
  group('Auth Screens', () {
    testWidgets('LoginScreen renders title', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: LoginScreen()),
      );
      expect(find.text('Login'), findsWidgets);
    });

    testWidgets('RegisterScreen renders title', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: RegisterScreen()),
      );
      expect(find.text('Register'), findsWidgets);
    });
  });
}
