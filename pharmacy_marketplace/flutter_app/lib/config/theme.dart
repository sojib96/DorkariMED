import 'package:flutter/material.dart';

class AppTheme {
  static const _primaryColor = Color(0xFF2563EB);
  static const _errorColor = Color(0xFFDC2626);
  static const _successColor = Color(0xFF16A34A);

  static ThemeData get light {
    return ThemeData(
      useMaterial3: true,
      colorSchemeSeed: _primaryColor,
      brightness: Brightness.light,
      scaffoldBackgroundColor: const Color(0xFFF9FAFB),
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        elevation: 0,
      ),
    );
  }

  static ThemeData get dark {
    return ThemeData(
      useMaterial3: true,
      colorSchemeSeed: _primaryColor,
      brightness: Brightness.dark,
    );
  }
}
